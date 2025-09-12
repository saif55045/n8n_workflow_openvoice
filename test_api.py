"""
Test script for OpenVoice API Server
"""
import requests
import json
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running?")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_list_voices():
    """Test listing voices"""
    try:
        response = requests.get(f"{API_BASE_URL}/voices")
        if response.status_code == 200:
            print("✅ List voices passed")
            print(f"Voices: {response.json()}")
        else:
            print(f"❌ List voices failed: {response.status_code}")
    except Exception as e:
        print(f"❌ List voices error: {e}")

def test_upload_voice(audio_file_path):
    """Test voice upload"""
    if not Path(audio_file_path).exists():
        print(f"❌ Audio file not found: {audio_file_path}")
        return
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': f}
            data = {'voice_name': 'test_voice'}
            response = requests.post(f"{API_BASE_URL}/upload-voice", files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Voice upload passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Voice upload failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Voice upload error: {e}")

def test_tts():
    """Test text-to-speech"""
    try:
        data = {
            'text': 'Hello, this is a test of the text-to-speech functionality.',
            'voice_name': 'default',
            'language': 'EN'
        }
        response = requests.post(f"{API_BASE_URL}/tts", data=data)
        
        if response.status_code == 200:
            print("✅ TTS test passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ TTS test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ TTS test error: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing OpenVoice API Server")
    print("=" * 50)
    
    # Test basic endpoints
    test_health_check()
    print()
    
    test_list_voices()
    print()
    
    test_tts()
    print()
    
    # Test voice upload if audio file exists
    sample_audio = "sample_voice.wav"
    if Path(sample_audio).exists():
        test_upload_voice(sample_audio)
    else:
        print(f"ℹ️  Skipping voice upload test - {sample_audio} not found")
    
    print("\n🏁 Testing completed!")

if __name__ == "__main__":
    main()
