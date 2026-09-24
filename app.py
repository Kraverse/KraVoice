import tempfile
from pathlib import Path

import streamlit as st
import whisper
from whisper.utils import get_writer

st.set_page_config(page_title="KraVoice", page_icon="🎙️")
st.title("KraVoice")
st.caption("AI audio transcription powered by Whisper")

@st.cache_resource
def load_model(name):
    return whisper.load_model(name)

mode = st.sidebar.radio("Input mode", ["Upload audio", "Audio URL"])
model_name = st.sidebar.selectbox("Whisper model", ["tiny", "base", "small", "medium", "large"], index=1)

if mode == "Upload audio":
    source = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "mp4", "mpeg", "webm"])
else:
    source = st.text_input("Audio or YouTube URL")

if source and st.button("Transcribe", type="primary"):
    try:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "audio"
            if mode == "Upload audio":
                path = path.with_suffix(Path(source.name).suffix)
                path.write_bytes(source.getvalue())
            else:
                import yt_dlp
                options = {"format": "bestaudio/best", "outtmpl": str(path) + ".%(ext)s"}
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([source])
                path = next(Path(folder).glob("audio.*"))

            with st.spinner(f"Loading {model_name} model..."):
                model = load_model(model_name)
            with st.spinner("Transcribing audio..."):
                result = model.transcribe(str(path))

            st.success(f"Detected language: {result['language']}")
            st.text_area("Transcript", result["text"].strip(), height=320)

            for fmt, mime in [("txt", "text/plain"), ("srt", "text/plain"), ("vtt", "text/vtt")]:
                if fmt == "txt":
                    data = result["text"].strip()
                else:
                    output = Path(folder) / fmt
                    output.mkdir()
                    get_writer(fmt, str(output))(result, str(path))
                    data = next(output.glob(f"*.{fmt}")).read_text(encoding="utf-8")
                st.download_button(f"Download {fmt.upper()}", data, f"transcript.{fmt}", mime=mime)
    except Exception as exc:
        st.error(f"Transcription failed: {exc}")
