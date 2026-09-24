# KraVoice

AI audio transcription app built with Python, Streamlit, and OpenAI Whisper.

## Features

- Audio and YouTube URL input
- Local audio upload
- Whisper model selection
- Automatic language detection
- TXT, SRT, and VTT exports
- Cached Whisper models
- Minimal Streamlit interface

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

FFmpeg is required by Whisper.

## Reference

KraVoice is based on the functionality of [AIAudioTranscriber](https://github.com/smaranjitghose/AIAudioTranscriber) by smaranjitghose.

The reference project is licensed under AGPL-3.0. KraVoice retains the applicable license and attribution requirements.
