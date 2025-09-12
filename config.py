"""
Configuration settings for OpenVoice API Server
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
VOICES_DIR = BASE_DIR / "voices"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# OpenVoice settings
OPENVOICE_V1_CHECKPOINT = CHECKPOINTS_DIR / "v1"
OPENVOICE_V2_CHECKPOINT = CHECKPOINTS_DIR / "v2"

# Audio settings
SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".flac", ".m4a", ".ogg"]
MAX_FILE_SIZE_MB = 50
SAMPLE_RATE = 22050

# Language settings
SUPPORTED_LANGUAGES = {
    "EN": "English",
    "ES": "Spanish", 
    "FR": "French",
    "ZH": "Chinese",
    "JA": "Japanese",
    "KO": "Korean"
}

# API settings
MAX_TEXT_LENGTH = 1000
DEFAULT_VOICE = "default"

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
