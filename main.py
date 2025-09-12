"""
OpenVoice FastAPI Server
A self-hosted OpenVoice API server using FastAPI for voice cloning and text-to-speech.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import shutil
import uuid
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime
import json
import torch
import librosa

# Add OpenVoice to Python path
sys.path.append('OpenVoice')

# Try importing OpenVoice modules
try:
    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS
    OPENVOICE_AVAILABLE = True
except ImportError as e:
    OPENVOICE_AVAILABLE = False
    print(f"[Warning] OpenVoice import failed: {e}")
    print("[Info] Running in dummy mode - OpenVoice functionality disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openvoice-server")

# Initialize FastAPI app
app = FastAPI(
    title="OpenVoice API Server",
    description="Self-hosted OpenVoice API for voice cloning and text-to-speech",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
VOICES_DIR = Path("voices")
CHECKPOINTS_DIR = Path("checkpoints")

for directory in [UPLOAD_DIR, OUTPUT_DIR, VOICES_DIR, CHECKPOINTS_DIR]:
    directory.mkdir(exist_ok=True)

# Global OpenVoice models
base_speaker_tts = None
tone_color_converter = None
device = None


async def initialize_openvoice_models():
    """Initialize OpenVoice models if available."""
    global base_speaker_tts, tone_color_converter, device

    if not OPENVOICE_AVAILABLE:
        logger.warning("OpenVoice not available - models not initialized")
        return

    try:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device}")

        # Initialize MeloTTS
        base_speaker_tts = TTS(language='EN', device=device)
        logger.info("Base TTS model initialized")

        # Initialize ToneColorConverter
        ckpt_converter = 'checkpoints/converter'
        if Path(ckpt_converter).exists():
            tone_color_converter = ToneColorConverter(
                f'{ckpt_converter}/config.json', device=device
            )
            tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
            logger.info("Tone color converter initialized")
        else:
            logger.warning(f"Converter checkpoint not found at {ckpt_converter}")
            logger.warning("Voice cloning will not be available")

    except Exception as e:
        logger.error(f"Failed to initialize OpenVoice models: {e}")


def extract_speaker_embedding(audio_path: str) -> Optional[torch.Tensor]:
    """Extract speaker embedding from uploaded audio."""
    if not OPENVOICE_AVAILABLE or tone_color_converter is None:
        return None
    try:
        speaker_embedding = se_extractor.get_se(
            audio_path, tone_color_converter, target_dir=str(OUTPUT_DIR), vad=True
        )
        return speaker_embedding
    except Exception as e:
        logger.error(f"Error extracting speaker embedding: {e}")
        return None


def generate_base_audio(text: str, output_path: str, language: str = 'EN', speed: float = 1.0) -> bool:
    """Generate base TTS audio using MeloTTS."""
    if not OPENVOICE_AVAILABLE or base_speaker_tts is None:
        return False
    try:
        base_speaker_tts.tts_to_file(
            text,
            base_speaker_tts.hps.data.spk2id['EN-US'],
            output_path,
            speed=speed
        )
        logger.info(f"Base audio generated: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating base audio: {e}")
        return False


def clone_voice_audio(base_audio_path: str, speaker_embedding: torch.Tensor, output_path: str) -> bool:
    """Apply voice cloning with tone color converter."""
    if not OPENVOICE_AVAILABLE or tone_color_converter is None:
        return False
    try:
        encode_message = "@MyShell"
        tone_color_converter.convert(
            audio_src_path=base_audio_path,
            src_se=speaker_embedding,
            tgt_se=speaker_embedding,
            output_path=output_path,
            message=encode_message
        )
        logger.info(f"Voice cloned: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error cloning voice: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Load OpenVoice models on startup."""
    logger.info("Starting OpenVoice API Server...")
    await initialize_openvoice_models()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "OpenVoice API Server",
        "version": "1.1.0"
    }


@app.post("/upload-voice")
async def upload_voice(file: UploadFile = File(...), voice_name: str = Form(...)):
    """Upload a reference voice for cloning."""
    try:
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")

        unique_filename = f"{voice_name}_{uuid.uuid4().hex}{Path(file.filename).suffix}"
        file_path = VOICES_DIR / unique_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        metadata = {
            "voice_name": voice_name,
            "file_path": str(file_path),
            "original_filename": file.filename,
            "upload_time": datetime.now().isoformat(),
            "file_size": file_path.stat().st_size
        }

        with open(VOICES_DIR / f"{voice_name}_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        return {"message": "Voice uploaded successfully", "voice_name": voice_name}
    except Exception as e:
        logger.error(f"Error uploading voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clone-voice")
async def clone_voice(text: str = Form(...), voice_name: str = Form(...), language: str = Form(default="EN")):
    """Clone uploaded voice with input text."""
    try:
        metadata_path = VOICES_DIR / f"{voice_name}_metadata.json"
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")

        with open(metadata_path, "r") as f:
            voice_metadata = json.load(f)

        voice_file_path = Path(voice_metadata["file_path"])
        if not voice_file_path.exists():
            raise HTTPException(status_code=404, detail="Voice file missing")

        # Extract embedding
        speaker_embedding = extract_speaker_embedding(str(voice_file_path))

        # Generate base audio
        base_audio_path = OUTPUT_DIR / f"base_{uuid.uuid4().hex}.wav"
        if not generate_base_audio(text, str(base_audio_path), language=language):
            raise HTTPException(status_code=500, detail="Base audio generation failed")

        # Try cloning
        output_path = OUTPUT_DIR / f"cloned_{voice_name}_{uuid.uuid4().hex}.wav"
        if speaker_embedding is not None and clone_voice_audio(str(base_audio_path), speaker_embedding, str(output_path)):
            pass  # success
        else:
            logger.warning("Falling back to base TTS (cloning unavailable)")
            shutil.copy(str(base_audio_path), str(output_path))

        # Cleanup
        if base_audio_path.exists():
            base_audio_path.unlink()

        return FileResponse(path=str(output_path), media_type="audio/wav", filename=output_path.name)

    except Exception as e:
        logger.error(f"Error in /clone-voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
async def text_to_speech(text: str = Form(...), language: str = Form(default="EN"), speed: float = Form(default=1.0)):
    """Simple text-to-speech (default synthetic voice)."""
    try:
        output_path = OUTPUT_DIR / f"tts_{uuid.uuid4().hex}.wav"

        if OPENVOICE_AVAILABLE and base_speaker_tts is not None:
            if generate_base_audio(text, str(output_path), language=language, speed=speed):
                return FileResponse(path=str(output_path), media_type="audio/wav", filename=output_path.name)
            else:
                raise HTTPException(status_code=500, detail="TTS generation failed")
        else:
            return {
                "message": "TTS dummy mode (OpenVoice not installed)",
                "text": text,
                "language": language,
                "speed": speed
            }
    except Exception as e:
        logger.error(f"Error in /tts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices")
async def list_voices():
    """List available uploaded voices."""
    voices = []
    for metadata_file in VOICES_DIR.glob("*_metadata.json"):
        with open(metadata_file, "r") as f:
            data = json.load(f)
            voices.append({
                "voice_name": data["voice_name"],
                "upload_time": data["upload_time"],
                "file_size": data["file_size"]
            })
    return {"voices": voices}


@app.delete("/voices/{voice_name}")
async def delete_voice(voice_name: str):
    """Delete a stored voice and metadata."""
    try:
        metadata_path = VOICES_DIR / f"{voice_name}_metadata.json"
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail=f"Voice '{voice_name}' not found")

        with open(metadata_path, "r") as f:
            voice_metadata = json.load(f)

        voice_file_path = Path(voice_metadata["file_path"])
        if voice_file_path.exists():
            voice_file_path.unlink()
        metadata_path.unlink()

        return {"message": f"Voice '{voice_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated audio files."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, media_type="audio/wav", filename=filename)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
