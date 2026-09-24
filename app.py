import streamlit as st
import whisper

st.set_page_config(page_title="KraVoice", page_icon="🎙️")
st.title("KraVoice")
st.caption("AI audio transcription powered by Whisper")

model_name = st.selectbox("Whisper model", ["tiny", "base", "small", "medium", "large"], index=1)
audio = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "mp4", "mpeg", "webm"])

if audio:
    st.audio(audio)
    if st.button("Transcribe", type="primary"):
        with st.spinner("Loading Whisper model..."):
            model = whisper.load_model(model_name)
        with st.spinner("Transcribing audio..."):
            result = model.transcribe(audio.name if False else audio.getvalue())
        text = result["text"].strip()
        st.subheader("Transcript")
        st.text_area("", text, height=300)
        st.download_button("Download TXT", text, "transcript.txt", "text/plain")
