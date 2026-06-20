# 🎙️ OpenVoice Voice Cloning — n8n Workflow Integration

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![n8n](https://img.shields.io/badge/n8n-Workflow_Automation-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

A self-hosted voice cloning API server powered by **OpenVoice**, integrated with **n8n** workflow automation for seamless text-to-speech (TTS) and voice cloning pipelines. This project provides a production-ready FastAPI backend with automated n8n workflows for voice upload, TTS generation, and voice cloning operations.

---

## 🖼️ Screenshots

![Screenshot](assets/Screenshot%202026-06-18%20210920.png)


## ✨ Features

- **🗣️ Text-to-Speech (TTS)** — Convert text to natural-sounding speech using OpenVoice's neural TTS engine.
- **🎭 Voice Cloning** — Clone any voice from a short audio sample and generate speech in the cloned voice.
- **🔄 n8n Workflow Automation** — Two pre-built n8n workflows for manual API testing and webhook-based file processing.
- **📤 Voice Upload Pipeline** — Upload reference audio files via API or n8n webhook for voice cloning.
- **🌐 Multi-Language Support** — Generate speech in multiple languages (EN, ES, FR, ZH, JP, KR).
- **🏗️ Production-Ready** — Configurable settings, health monitoring, error handling, and structured logging.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **API Server** | Python, FastAPI |
| **Voice Engine** | OpenVoice (MyShell AI) |
| **Workflow Automation** | n8n |
| **Testing** | pytest, API test scripts |
| **Configuration** | Pydantic Settings |

---

## 📦 Getting Started

### Prerequisites
- Python 3.9+
- n8n (installed globally via npm)
- GPU recommended for faster inference

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/saif55045/n8n_workflow_openvoice.git
   cd n8n_workflow_openvoice
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python setup_openvoice.py
   ```

3. **Start the API server:**
   ```bash
   python main.py
   # Server runs on http://localhost:8000
   ```

4. **Start n8n and import workflows:**
   ```bash
   n8n start
   # Import n8n_workflow.json in the n8n UI
   ```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/upload-voice` | POST | Upload a reference voice sample |
| `/clone-voice` | POST | Clone voice with custom text |
| `/tts` | POST | Text-to-speech generation |
| `/voices` | GET | List all uploaded voices |
| `/voices/{name}` | DELETE | Remove a voice |

---

## 📐 Project Structure

```
n8n_workflow_openvoice/
├── main.py                  # FastAPI server entry point
├── app.py                   # Application logic & route handlers
├── config.py                # Environment configuration
├── models.py                # Pydantic request/response models
├── production.py            # Production deployment settings
├── setup_openvoice.py       # OpenVoice model setup script
├── test_api.py              # API endpoint tests
├── n8n_workflow.json         # n8n manual trigger workflow
├── requirements.txt          # Python dependencies
├── voices/                   # Uploaded voice samples
├── outputs/                  # Generated audio files
├── checkpoints/              # Model checkpoints
└── N8N_WORKFLOW_DOCUMENTATION.md  # Detailed workflow docs
```

> 📖 For detailed n8n workflow usage, see [N8N_WORKFLOW_DOCUMENTATION.md](N8N_WORKFLOW_DOCUMENTATION.md).

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

