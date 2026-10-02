# 🎙️ KraVoice

**AI-powered audio transcription built by Kraverse.**

Turn recordings and supported video/audio sources into clean, timestamped text using OpenAI Whisper.

## 🚀 Live Demo

**KraVoice:** https://kravoice.streamlit.app/

## ✨ Features

- 🎙️ Upload MP3, WAV, M4A, MP4, MPEG, and WebM files
- ▶️ YouTube URL support when captions are accessible
- 🔗 Direct audio URL support
- 🤖 OpenAI Whisper transcription
- 🧠 Tiny, Base, Small, Medium, and Large models
- 🌐 Automatic language detection
- 📄 TXT transcript export
- 🎬 SRT subtitle export
- 🎬 VTT subtitle export
- ⚡ Simple Streamlit interface
- 🛡️ Clear handling for unsupported Spotify/blocked YouTube requests
- 🐳 Docker-ready
- ✅ GitHub Actions CI

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| OpenAI Whisper | Speech-to-text |
| yt-dlp | Supported media URL extraction |
| YouTube Transcript API | YouTube caption retrieval |
| FFmpeg | Audio processing |
| GitHub Actions | CI validation |
| Docker | Containerized deployment |

## 🔄 How It Works

```text
Audio / URL
    ↓
Input validation
    ↓
Whisper / YouTube captions
    ↓
Language detection
    ↓
Transcript
    ↓
TXT / SRT / VTT
```

## 💻 Run Locally

### 1. Clone

```bash
git clone https://github.com/Kraverse/KraVoice.git
cd KraVoice
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

Whisper requires FFmpeg for audio processing.

### 4. Start KraVoice

```bash
streamlit run app.py
```

Open the local Streamlit URL shown in your terminal.

## 📁 Project Structure

```text
KraVoice/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .streamlit/
│   └── config.toml
├── app.py
├── Dockerfile
├── LICENSE
├── README.md
└── requirements.txt
```

## ⚠️ YouTube Note

YouTube can restrict media downloads from cloud-hosted environments with HTTP 403 responses. KraVoice therefore attempts accessible YouTube captions first. Uploaded audio and supported direct audio URLs remain available for Whisper transcription.

Spotify links are not supported because Spotify audio is DRM-protected.

## 📜 License & Attribution

KraVoice is based on the functionality of the open-source **AIAudioTranscriber** project by **smaranjitghose**.

Reference repository:
https://github.com/smaranjitghose/AIAudioTranscriber

The reference project is licensed under **AGPL-3.0**. This repository retains the applicable license and attribution requirements.

See `LICENSE` for the project license information.

## 👨‍💻 Author

**Kartik Suresh Katke — Kraverse**

GitHub: https://github.com/Kraverse

LinkedIn: https://www.linkedin.com/in/kraverse

---

⭐ If KraVoice is useful, consider starring the repository.
