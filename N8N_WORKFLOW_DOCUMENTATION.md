# OpenVoice n8n Workflow Documentation

This document provides comprehensive instructions for using the n8n workflows with the OpenVoice API server.

## Overview

The OpenVoice project includes two main n8n workflows:

1. **Main API Workflow** (`n8n_workflow.json`) - Manual trigger workflow for testing all API endpoints
2. **File Upload Workflow** (`n8n_file_upload_workflow.json`) - Webhook-based workflow for file uploads and text processing

## Prerequisites

### 1. OpenVoice API Server Setup
Ensure the OpenVoice API server is running on `http://localhost:8000`:

```bash
cd openvoice-api
python main.py
```

### 2. n8n Installation and Setup
Install and start n8n:

```bash
npm install -g n8n
n8n start
```

Access n8n at: `http://localhost:5678`

## Workflow 1: Main API Workflow (Manual Trigger)

### Import the Workflow
1. Open n8n in your browser
2. Click "Import from file" 
3. Select `n8n_workflow.json`
4. Save the workflow

### Usage Instructions

This workflow uses a manual trigger and supports the following operations:

#### Available Operations
- `health_check` - Test API server health
- `tts` - Text-to-speech conversion
- `clone_voice` - Voice cloning with uploaded voices
- `list_voices` - List all uploaded voices

#### How to Use

1. **Configure Parameters**: Edit the "Set Parameters" node to specify:
   ```json
   {
     "operation": "health_check|tts|clone_voice|list_voices",
     "text": "Your text for TTS or voice cloning",
     "language": "EN",
     "speed": "1.0",
     "voice_name": "name_of_uploaded_voice"
   }
   ```

2. **Execute the Workflow**: Click "Execute Workflow" button

3. **View Results**: Check the "Format Response" node output for results

#### Example Configurations

**Health Check:**
```json
{
  "operation": "health_check"
}
```

**Text-to-Speech:**
```json
{
  "operation": "tts",
  "text": "Hello, this is a test message.",
  "language": "EN",
  "speed": "1.0"
}
```

**Voice Cloning:**
```json
{
  "operation": "clone_voice", 
  "text": "Clone this text with my voice",
  "voice_name": "my_uploaded_voice",
  "language": "EN"
}
```

**List Voices:**
```json
{
  "operation": "list_voices"
}
```

## Workflow 2: File Upload Workflow (Webhooks)

### Import the Workflow
1. Import `n8n_file_upload_workflow.json` into n8n
2. Save and activate the workflow

### Webhook Endpoints

After activation, you'll get two webhook URLs:

1. **Voice Upload Webhook**: `http://localhost:5678/webhook/upload-voice`
2. **Text File Processing Webhook**: `http://localhost:5678/webhook/process-text-file`

### Usage Instructions

#### Voice Upload
Upload audio files for voice cloning:

```bash
curl -X POST "http://localhost:5678/webhook/upload-voice" \
  -F "voice_name=my_voice" \
  -F "file=@path/to/voice.wav"
```

#### Text File Processing
Upload text files for TTS or voice cloning:

```bash
# For TTS
curl -X POST "http://localhost:5678/webhook/process-text-file" \
  -F "operation=tts" \
  -F "language=EN" \
  -F "file=@path/to/text.txt"

# For Voice Cloning
curl -X POST "http://localhost:5678/webhook/process-text-file" \
  -F "operation=clone_voice" \
  -F "voice_name=my_voice" \
  -F "language=EN" \
  -F "file=@path/to/text.txt"
```

## API Endpoints Reference

The workflows interact with these OpenVoice API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/upload-voice` | POST | Upload voice for cloning |
| `/clone-voice` | POST | Clone voice with text |
| `/tts` | POST | Text-to-speech |
| `/voices` | GET | List uploaded voices |
| `/voices/{name}` | DELETE | Delete a voice |

## Expected Responses

### Health Check Response
```json
{
  "operation": "health_check",
  "timestamp": "2024-01-01T12:00:00Z",
  "success": true,
  "status": "ok",
  "service": "OpenVoice API Server",
  "version": "1.1.0"
}
```

### TTS Response
```json
{
  "operation": "tts",
  "timestamp": "2024-01-01T12:00:00Z",
  "success": true,
  "message": "TTS audio generated successfully",
  "audio_available": true
}
```

### Voice Cloning Response
```json
{
  "operation": "clone_voice",
  "timestamp": "2024-01-01T12:00:00Z", 
  "success": true,
  "message": "Voice cloning completed successfully",
  "audio_available": true
}
```

### List Voices Response
```json
{
  "operation": "list_voices",
  "timestamp": "2024-01-01T12:00:00Z",
  "success": true,
  "voices": [
    {
      "voice_name": "my_voice",
      "upload_time": "2024-01-01T11:00:00Z",
      "file_size": 1024000
    }
  ],
  "voice_count": 1
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure OpenVoice API server is running on port 8000
   - Check if server started successfully without errors

2. **Voice Not Found**
   - Upload voice files first using the upload workflow
   - Verify voice name matches uploaded voice

3. **OpenVoice Import Errors**
   - Ensure OpenVoice is properly installed in the virtual environment
   - Check that required model checkpoints are downloaded

4. **Audio Generation Fails**
   - Check server logs for detailed error messages
   - Ensure sufficient system resources (RAM/GPU)

### Monitoring Workflow Execution

1. Check workflow execution history in n8n
2. Monitor API server logs for errors
3. Use the health check endpoint to verify server status

## Integration with External Applications

These workflows can be integrated with external applications by:

1. **Using Webhook URLs** - Direct HTTP requests to workflow webhooks
2. **API Calls** - Chain multiple operations using the manual trigger workflow
3. **File Processing** - Batch process text files through the file upload workflow

## Security Considerations

- Run n8n and OpenVoice API on trusted networks only
- Implement authentication for production deployments
- Validate file uploads to prevent security issues
- Monitor resource usage to prevent abuse

## Project Requirements Alignment

This workflow implementation fulfills the project requirements:

✅ **Self-hosted OpenVoice API server** - FastAPI server with all required endpoints
✅ **Proper project structure** - Organized codebase with clear separation
✅ **n8n Integration** - Complete workflows for API interaction
✅ **Manual trigger support** - No dependency on Streamlit frontend
✅ **File upload handling** - Support for text files and audio files
✅ **Voice cloning pipeline** - Complete workflow from upload to cloned audio
✅ **Production ready** - Error handling, logging, and monitoring

The workflows provide a complete automation solution for OpenVoice operations without requiring the Streamlit frontend, using manual triggers and webhooks as specified in the requirements.
