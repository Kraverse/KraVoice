import tempfile
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
import whisper
from whisper.utils import get_writer

st.set_page_config(page_title="KraVoice", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
.stApp { background:#050505; color:#f5f5f5; }
.block-container { max-width:1100px; padding:2rem 2rem 4rem; }
.nav { display:flex; justify-content:space-between; align-items:center; padding:8px 0 55px; }
.logo { font-size:24px; font-weight:700; letter-spacing:-1px; }
.logo span { color:#a78bfa; }
.navlinks { background:#181818; border:1px solid #292929; border-radius:10px; padding:11px 22px; color:#aaa; font-size:12px; }
.cta { background:#fff; color:#111; padding:11px 20px; border-radius:9px; font-size:13px; font-weight:600; }
.hero { text-align:center; padding:15px 0 35px; }
.hero h1 { font-size:52px; line-height:1.08; letter-spacing:-2px; margin:0 auto 18px; max-width:780px; }
.hero h1 b { color:#fff; }
.hero p { color:#858585; font-size:15px; line-height:1.7; max-width:620px; margin:auto; }
.wave { height:105px; display:flex; align-items:center; justify-content:center; gap:5px; margin:20px auto 35px; overflow:hidden; }
.bar { width:5px; background:#292929; border-radius:5px; }
.panel { background:#101010; border:1px solid #252525; border-radius:18px; padding:25px; }
.section-title { font-size:22px; font-weight:650; margin-bottom:5px; }
.section-copy { color:#777; font-size:13px; margin-bottom:20px; }
.feature { background:#101010; border:1px solid #222; border-radius:15px; padding:22px; min-height:120px; }
.feature h3 { margin:0 0 8px; font-size:16px; }
.feature p { color:#777; font-size:13px; line-height:1.6; }
footer { text-align:center; color:#555; padding-top:50px; font-size:12px; }
button[kind="primary"] { border-radius:9px; }
</style>
""", unsafe_allow_html=True)

bars = [22, 38, 62, 30, 76, 46, 92, 34, 68, 48, 82, 28, 60, 42, 96, 35, 72, 50, 88, 30, 66, 44, 78, 36, 58, 42, 90, 28, 70, 48, 84, 32]
wave = "".join(f'<div class="bar" style="height:{h}%"></div>' for h in bars)

st.markdown(f"""
<div class="nav">
  <div class="logo">Kra<span>Voice</span></div>
  <div class="navlinks">Home &nbsp;&nbsp;&nbsp; How it works &nbsp;&nbsp;&nbsp; Features &nbsp;&nbsp;&nbsp; Pricing</div>
  <div class="cta">Get Started</div>
</div>
<div class="hero">
  <h1>Turn spoken words into <b>smart text.</b></h1>
  <p>AI-powered transcription that listens, understands, and turns your audio into accurate text in seconds.</p>
</div>
<div class="wave">{wave}</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
left, right = st.columns([1.6, 1])
with left:
    st.markdown('<div class="section-title">Transcribe your audio</div><div class="section-copy">Upload a file or paste a YouTube / direct audio URL.</div>', unsafe_allow_html=True)
    mode = st.radio("Input", ["Upload audio", "Audio URL"], horizontal=True, label_visibility="collapsed")
    if mode == "Upload audio":
        source = st.file_uploader("Drop audio here", type=["mp3", "wav", "m4a", "mp4", "mpeg", "webm"])
    else:
        source = st.text_input("YouTube or direct audio URL", placeholder="https://youtube.com/... or https://example.com/audio.mp3")
with right:
    st.markdown('<div class="section-title">Whisper model</div><div class="section-copy">Choose speed or accuracy.</div>', unsafe_allow_html=True)
    model_name = st.selectbox("Model", ["tiny", "base", "small", "medium", "large"], index=1, label_visibility="collapsed")
    st.caption("Larger models generally improve accuracy but need more memory and time.")
st.markdown('</div>', unsafe_allow_html=True)
st.write("")

if source and st.button("Start transcription", type="primary", use_container_width=True):
    try:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "audio"
            if mode == "Upload audio":
                path = path.with_suffix(Path(source.name).suffix)
                path.write_bytes(source.getvalue())
            else:
                host = urlparse(source).netloc.lower()
                if "spotify.com" in host:
                    st.error("Spotify links are DRM-protected and cannot be downloaded for transcription. Use an uploaded audio file, YouTube URL, or direct audio URL instead.")
                    st.stop()
                import yt_dlp
                options = {
                    "format": "bestaudio/best",
                    "outtmpl": str(path) + ".%(ext)s",
                    "noplaylist": True,
                    "quiet": True,
                    "extractor_args": {"youtube": {"player_client": ["web_safari", "android_vr"]}},
                }
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([source])
                files = list(Path(folder).glob("audio.*"))
                if not files:
                    raise RuntimeError("No audio stream was downloaded from this URL.")
                path = files[0]

            with st.spinner(f"Loading {model_name} model..."):
                model = whisper.load_model(model_name)
            with st.spinner("Transcribing audio..."):
                result = model.transcribe(str(path))

            st.success(f"Detected language: {result['language']}")
            st.text_area("Transcript", result["text"].strip(), height=320)

            cols = st.columns(3)
            for col, fmt, mime in zip(cols, ["txt", "srt", "vtt"], ["text/plain", "text/plain", "text/vtt"]):
                if fmt == "txt":
                    data = result["text"].strip()
                else:
                    output = Path(folder) / fmt
                    output.mkdir()
                    get_writer(fmt, str(output))(result, str(path))
                    data = next(output.glob(f"*.{fmt}")).read_text(encoding="utf-8")
                col.download_button(f"Download {fmt.upper()}", data, f"transcript.{fmt}", mime=mime, use_container_width=True)
    except Exception as exc:
        message = str(exc)
        if "403" in message and "youtube" in source.lower():
            message = "YouTube rejected the hosted download request (HTTP 403). Try uploading the audio file or use a direct audio URL."
        st.error(f"Transcription failed: {message}")

st.markdown("""
<div style="height:45px"></div>
<div class="hero"><h2>Everything you need to work with voice.</h2><p>Simple tools for turning recordings, lectures, and videos into useful text.</p></div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, title, text in [
    (c1, "Fast transcription", "Whisper-powered speech recognition with selectable model sizes."),
    (c2, "Multiple formats", "Export clean transcripts as TXT, SRT, or VTT subtitles."),
    (c3, "Simple workflow", "Upload audio or use a supported URL and get your transcript in one place."),
]:
    with col:
        st.markdown(f'<div class="feature"><h3>{title}</h3><p>{text}</p></div>', unsafe_allow_html=True)

st.markdown('<footer>KraVoice · AI audio transcription by Kraverse</footer>', unsafe_allow_html=True)
