"""
Pydantic models for OpenVoice API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str

class VoiceUploadResponse(BaseModel):
    message: str
    voice_name: str
    file_path: str

class VoiceCloneRequest(BaseModel):
    text: str = Field(..., description="Text to be spoken")
    voice_name: str = Field(..., description="Name of the voice to clone")
    language: str = Field(default="EN", description="Language code (EN, ES, FR, etc.)")

class VoiceCloneResponse(BaseModel):
    message: str
    text: str
    voice_name: str
    language: str
    output_file: str

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to be converted to speech")
    voice_name: str = Field(default="default", description="Voice name to use")
    language: str = Field(default="EN", description="Language code")
    speed: float = Field(default=1.0, description="Speech speed multiplier")

class TTSResponse(BaseModel):
    message: str
    text: str
    voice_name: str
    language: str
    speed: float
    output_file: str

class VoiceInfo(BaseModel):
    voice_name: str
    upload_time: str
    file_size: int

class VoicesListResponse(BaseModel):
    voices: List[VoiceInfo]

class DeleteVoiceResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
