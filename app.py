import base64
import re
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import streamlit as st
import whisper
from whisper.utils import get_writer

st.set_page_config(page_title="KraVoice", page_icon="🎙️", layout="wide")

# ---------------------------------------------------------------- design system
st.markdown("""
<style>
:root{
  --bg:#050505; --surface:#0d0d0d; --surface2:#141414; --line:#232323; --line2:#2e2e2e;
  --text:#f2f2f2; --muted:#9a9a9a; --faint:#6a6a6a; --accent:#a78bfa; --accent-soft:rgba(167,139,250,.12);
  --r-sm:8px; --r-md:12px; --r-lg:20px; --ease:cubic-bezier(.22,.61,.36,1);
}
.stApp{background:var(--bg);color:var(--text);}
.block-container{max-width:1040px;padding:1.6rem 1.5rem 4rem;}
@media(max-width:640px){.block-container{padding:1rem .9rem 3rem;}}
html{scroll-behavior:smooth;}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}html{scroll-behavior:auto;}}

/* ---------- navigation ---------- */
.nav{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 0 60px;}
.logo{font-size:22px;font-weight:600;letter-spacing:-.5px;color:var(--text);white-space:nowrap;}
.logo span{color:var(--accent);}
.navlinks{display:flex;gap:4px;background:rgba(20,20,20,.72);border:1px solid var(--line);
  border-radius:999px;padding:6px 10px;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);}
.navlinks span{color:var(--muted);font-size:12.5px;padding:7px 14px;border-radius:999px;transition:color .2s var(--ease),background .2s var(--ease);}
.navlinks span:hover{color:var(--text);background:rgba(255,255,255,.05);}
.navlinks a{color:inherit;text-decoration:none;}
.navcta{background:#fff;color:#111!important;text-decoration:none!important;font-size:13px;font-weight:600;padding:10px 20px;border-radius:999px;display:inline-block;line-height:1.2;box-shadow:none!important;
  transition:transform .2s var(--ease),box-shadow .2s var(--ease);white-space:nowrap;}
.navcta:hover{transform:translateY(-1px);box-shadow:0 6px 24px rgba(255,255,255,.12)!important;}
.stApp a[href^="#"], .stApp a[href^="data:"]{color:inherit;}
div[data-testid="stMarkdownContainer"] a[class]{color:inherit;}
@media(max-width:760px){.navlinks{display:none;}}

/* ---------- hero ---------- */
.hero{text-align:center;padding:12px 0 8px;position:relative;}
.hero a, a.btn-primary, a.btn-ghost, a.navcta{color:#111;text-decoration:none;}
a.btn-ghost{color:var(--text)!important;}
.hero h1{font-size:clamp(34px,5.4vw,58px);line-height:1.1;letter-spacing:-1.8px;font-weight:600;
  margin:0 auto 18px;max-width:760px;color:var(--text);}
.hero h1 b{color:var(--accent);font-weight:600;}
.hero p{color:var(--muted);font-size:15.5px;line-height:1.7;max-width:600px;margin:0 auto;}
.hero-ctas{display:flex;gap:12px;justify-content:center;margin:28px 0 8px;flex-wrap:wrap;}
a.btn-primary,a.btn-ghost{text-decoration:none!important;}
.btn-primary{background:#fff;color:#111!important;font-size:14px;font-weight:600;padding:13px 28px;border-radius:999px;
  transition:transform .2s var(--ease),box-shadow .2s var(--ease);}
.btn-primary:hover{transform:translateY(-1px);box-shadow:0 8px 28px rgba(255,255,255,.14);}
.btn-ghost{border:1px solid var(--line2);color:var(--text)!important;font-size:14px;font-weight:500;padding:13px 28px;
  border-radius:999px;transition:border-color .2s var(--ease),background .2s var(--ease);}
.btn-ghost:hover{border-color:#454545;background:rgba(255,255,255,.04);}
a.btn-primary,a.btn-ghost{text-decoration:none;display:inline-block;}
a.btn-primary:focus-visible,a.btn-ghost:focus-visible,.navcta:focus-visible{outline:2px solid var(--accent);outline-offset:3px;}

/* ---------- waveform ---------- */
.wave{height:96px;display:flex;align-items:center;justify-content:center;gap:4px;margin:26px auto 30px;overflow:hidden;}
.wave .bar{width:4px;border-radius:4px;background:linear-gradient(to top,#2b2b2b,#3d3d3d);
  animation:breathe 3.4s var(--ease) infinite alternate;}
@keyframes breathe{from{transform:scaleY(.55);opacity:.55;}to{transform:scaleY(1);opacity:1;}}
.wave.listening .bar{background:linear-gradient(to top,#7c3aed,#a78bfa);animation-duration:1.1s;}
.wave.processing .bar{background:linear-gradient(to top,#6d5bb8,#a78bfa);animation-duration:1.8s;}
.wave.error .bar{background:linear-gradient(to top,#5a2b2b,#8a4444);animation:none;opacity:.7;}

/* ---------- workspace ---------- */
div[data-testid="stVerticalBlock"]{gap:.75rem;}
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"],
div[data-testid="stElementContainer"] div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]{background:rgba(16,16,16,.82);border:1px solid var(--line) !important;
  border-radius:var(--r-lg) !important;padding:28px !important;box-shadow:0 20px 60px rgba(0,0,0,.45);
  backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);}
@media(max-width:640px){
  div[data-testid="stVerticalBlockBorderWrapper"],
  div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]{padding:18px !important;}}
.section-title{font-size:20px;font-weight:600;letter-spacing:-.3px;margin-bottom:4px;}
.section-copy{color:var(--muted);font-size:13px;line-height:1.6;margin-bottom:18px;}
.step-label{display:inline-flex;align-items:center;gap:8px;color:var(--faint);font-size:11px;font-weight:600;
  letter-spacing:1.4px;text-transform:uppercase;margin-bottom:10px;}
.step-label i{width:6px;height:6px;border-radius:50%;background:var(--accent);display:inline-block;}

/* results */
.result-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:6px 0 14px;}
.chip{display:inline-flex;align-items:center;gap:7px;background:var(--accent-soft);color:var(--accent);
  border:1px solid rgba(167,139,250,.25);border-radius:999px;padding:5px 13px;font-size:12px;font-weight:600;}
.result-actions{display:flex;gap:8px;flex-wrap:wrap;}
.feature{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);padding:22px;
  min-height:110px;transition:border-color .2s var(--ease),transform .2s var(--ease);}
.feature:hover{border-color:var(--line2);transform:translateY(-2px);}
.feature h3{margin:0 0 8px;font-size:15.5px;font-weight:600;}
.feature p{color:var(--muted);font-size:13px;line-height:1.6;}

/* ---------- streamlit widget theming ---------- */
button[kind="primary"]{background:#fff!important;color:#111!important;border:none!important;
  border-radius:999px!important;font-weight:600!important;padding:11px 24px!important;
  transition:transform .2s var(--ease),box-shadow .2s var(--ease)!important;}
button[kind="primary"]:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(255,255,255,.12);}
button[kind="primary"]:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
button[kind="secondary"], button[kind="secondaryFormSubmit"]{border-radius:999px!important;border:1px solid var(--line2)!important;}
.stButton>button,.stDownloadButton>button{transition:transform .2s var(--ease),box-shadow .2s var(--ease),border-color .2s var(--ease);}
.stDownloadButton>button:hover,.stButton>button[kind="secondary"]:hover{border-color:#454545!important;transform:translateY(-1px);}
[data-baseweb="radio"]{gap:0;}
div[role="radiogroup"]{gap:8px;}
div[role="radiogroup"] label{background:var(--surface2);border:1px solid var(--line);border-radius:999px;
  padding:7px 16px;margin:0;transition:border-color .2s var(--ease),background .2s var(--ease);}
div[role="radiogroup"] label:hover{border-color:#454545;}
div[role="radiogroup"] label[data-checked="true"]{border-color:var(--accent);background:var(--accent-soft);}
div[role="radiogroup"] label div{color:var(--muted);font-size:13px;}
div[role="radiogroup"] label[data-checked="true"] div{color:var(--text);}
div[data-testid="stFileUploaderDropzone"]{border-radius:var(--r-md);border:1px dashed var(--line2);background:var(--surface);}
div[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--accent);}
.stTextInput input,.stTextArea textarea{border-radius:var(--r-sm);}
.stTabs [data-baseweb="tab-list"]{gap:2px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{border-radius:8px 8px 0 0;}
footer{border-top:1px solid var(--line);margin-top:56px;}
footer .block-container{padding-top:1.2rem;padding-bottom:1.6rem;}
.visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- hero / nav
NAV_LINKS = [("How it works", "workspace"), ("Features", "features")]
navlinks = "".join(f'<span><a href="#{anchor}">{label}</a></span>' for label, anchor in NAV_LINKS)

st.markdown(f"""
<div class="nav">
  <div class="logo">Kra<span>Voice</span></div>
  <div class="navlinks">{navlinks}</div>
  <a class="navcta" href="#workspace">Get Started</a>
</div>
<div class="hero">
  <h1>Turn spoken words into <b>smart text.</b></h1>
  <p>KraVoice listens to your recordings, lectures, and videos — and returns clean, structured transcripts in seconds. Record, upload, or paste a link.</p>
  <div class="hero-ctas">
    <a class="btn-primary" href="#workspace">Start transcribing</a>
    <a class="btn-ghost" href="#features">Learn more</a>
  </div>
</div>
""", unsafe_allow_html=True)

WAVE_BARS = [22,38,62,30,76,46,92,34,68,48,82,28,60,42,96,35,72,50,88,30,66,44,78,36,58,42,90,28,70,48,84,32]
wave_html = "".join(f'<div class="bar" style="height:{h}%;animation-delay:{i*0.09:.2f}s"></div>' for i, h in enumerate(WAVE_BARS))
st.markdown(f'<div class="wave" id="krawave" aria-hidden="true">{wave_html}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- workspace
with st.container(border=True):
    st.markdown('<div class="step-label"><i></i>Step 1 · Provide audio</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Transcribe your audio</div>'
                '<div class="section-copy">Record from your microphone, upload a file, or paste a YouTube / direct audio URL.</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1.7, 1])
with left:
    mode = st.radio("Input", ["Record", "Upload audio", "Audio URL"], horizontal=True, label_visibility="collapsed")
    if mode == "Record":
        st.markdown('<div class="section-copy" style="margin:10px 0 0">Press the button below and speak. Your audio is processed in-memory and never stored.</div>', unsafe_allow_html=True)
        source = st.audio_input("Record your voice", key="rec")
    elif mode == "Upload audio":
        source = st.file_uploader("Drop audio here", type=["mp3", "wav", "m4a", "mp4", "mpeg", "webm"])
    else:
        source = st.text_input("YouTube or direct audio URL",
                               placeholder="https://youtube.com/... or https://example.com/audio.mp3")
        if source and not urlparse(source).netloc:
            st.markdown('<div class="chip" style="color:#d99;border-color:rgba(217,153,153,.3);background:rgba(217,153,153,.08)">⚠ That doesn’t look like a valid URL yet</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="step-label"><i></i>Step 2 · Choose a model</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="font-size:16px">Whisper model</div>'
                '<div class="section-copy" style="margin-bottom:12px">Speed or accuracy — your call.</div>', unsafe_allow_html=True)
    model_name = st.selectbox("Model", ["tiny", "base", "small", "medium", "large"], index=1, label_visibility="collapsed")
    st.caption("Larger models generally improve accuracy but need more memory and time.")

    go = st.button("Start transcription", type="primary", use_container_width=True, disabled=not source)

if not source and not go:
    st.markdown('<div class="section-copy" style="margin:14px 0 0;text-align:center">'
                '↑ Provide audio above to begin — nothing has been submitted yet.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- transcription logic (unchanged behavior)
if go and source:
    try:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "audio"
            result = None
            youtube = False

            st.markdown('<div class="step-label" style="margin-top:26px"><i></i>Processing</div>', unsafe_allow_html=True)

            if mode == "Record":
                suffix = Path(source.name).suffix or ".wav"
                path = path.with_suffix(suffix)
                path.write_bytes(source.getvalue())
            elif mode == "Upload audio":
                path = path.with_suffix(Path(source.name).suffix)
                path.write_bytes(source.getvalue())
            else:
                host = urlparse(source).netloc.lower()
                if "spotify.com" in host:
                    st.markdown('<div class="wave error" aria-hidden="true">' + wave_html + '</div>', unsafe_allow_html=True)
                    st.error("Spotify links are DRM-protected. Upload the audio file or use a supported direct audio URL.")
                    st.stop()

                youtube = "youtube.com" in host or "youtu.be" in host
                if youtube:
                    match = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", source)
                    video_id = match.group(1) if match else parse_qs(urlparse(source).query).get("v", [""])[0]
                    if not video_id:
                        raise RuntimeError("Could not read the YouTube video ID.")
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        transcript = YouTubeTranscriptApi().fetch(video_id)
                        result = {"language": transcript.language_code, "segments": [{"start": s.start, "end": s.start + s.duration, "text": s.text} for s in transcript.snippets]}
                        result["text"] = " ".join(s["text"] for s in result["segments"])
                    except Exception as exc:
                        raise RuntimeError("YouTube captions could not be accessed from this hosted app. Streamlit Cloud uses a cloud IP that YouTube may block. Upload the audio file, use a direct audio URL, or run KraVoice locally for YouTube audio downloads.") from exc
                else:
                    import yt_dlp
                    options = {"format":"bestaudio/best", "outtmpl":str(path)+".%(ext)s", "noplaylist":True, "quiet":True}
                    with yt_dlp.YoutubeDL(options) as ydl:
                        ydl.download([source])
                    files = list(Path(folder).glob("audio.*"))
                    if not files:
                        raise RuntimeError("No audio stream was downloaded from this URL.")
                    path = files[0]

            if result is None:
                with st.status(f"Loading the {model_name} model…", expanded=False) as status:
                    model = whisper.load_model(model_name)
                    status.update(label="Transcribing your audio…", state="running")
                    result = model.transcribe(str(path))
                    status.update(label="Transcription complete", state="complete", expanded=False)

        # ---------------- results (outside temp dir lifetime)
        st.markdown('<div class="step-label" style="margin-top:26px"><i></i>Step 3 · Result</div>', unsafe_allow_html=True)
        text = result["text"].strip()
        st.markdown(f"""
<div class="result-head">
  <span class="chip">● Detected language: {result['language']}</span>
</div>""", unsafe_allow_html=True)
        st.text_area("Transcript", text, height=320)
        st.caption(f"{len(text.split())} words · {len(result.get('segments', []))} segments")

        st.markdown('<div class="result-actions">', unsafe_allow_html=True)
        dl_cols = st.columns(3)
        if youtube:
            def stamp(t, comma=True):
                h, t = divmod(t, 3600); m, t = divmod(t, 60); s, ms = divmod(t, 1)
                return f"{int(h):02}:{int(m):02}:{int(s):02}{',' if comma else '.'}{int(ms*1000):03}"
            srt = "\n\n".join(f"{i}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{x['text']}" for i, x in enumerate(result["segments"], 1))
            vtt = "WEBVTT\n\n" + srt.replace(",", ".")
            downloads = [("TXT", text, "text/plain"), ("SRT", srt, "text/plain"), ("VTT", vtt, "text/vtt")]
        else:
            downloads = []
            with tempfile.TemporaryDirectory() as folder2:
                p2 = Path(folder2) / "audio" + path.suffix
                p2.write_bytes(path.read_bytes())
                for fmt in ["txt", "srt", "vtt"]:
                    if fmt == "txt":
                        data = text
                    else:
                        output = Path(folder2) / fmt; output.mkdir(); get_writer(fmt, str(output))(result, str(p2)); files = list(output.glob(f"*.{fmt}")); data = files[0].read_text(encoding="utf-8")
                    downloads.append((fmt.upper(), data, "text/vtt" if fmt == "vtt" else "text/plain"))
        for col, (name, data, mime) in zip(dl_cols, downloads):
            col.download_button(f"Download {name}", data, f"transcript.{name.lower()}", mime=mime, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        b64 = base64.b64encode(text.encode()).decode()
        st.markdown(f'<a class="btn-ghost" href="data:text/plain;base64,{b64}" download="transcript.txt" style="margin-top:14px;display:inline-block">⧉ Download transcript as .txt</a>', unsafe_allow_html=True)

    except Exception as exc:
        st.markdown('<div class="wave error" aria-hidden="true">' + wave_html + '</div>', unsafe_allow_html=True)
        st.error(f"Transcription failed: {exc}")
        st.info("You can try a different source, switch to a smaller model, or upload the audio file directly.")

# ---------------------------------------------------------------- features / footer
st.markdown('<div style="height:48px"></div><div class="hero" id="features"><h1 style="font-size:clamp(26px,3.4vw,36px)">Everything you need to work with voice.</h1>'
            '<p>Simple tools for turning recordings, lectures, and videos into useful text.</p></div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
for col, title, text_ in [
    (c1, "Fast transcription", "Whisper-powered speech recognition with selectable model sizes, from instant drafts to maximum accuracy."),
    (c2, "Multiple formats", "Export clean transcripts as TXT, SRT, or VTT subtitles — ready for editing, captioning, or publishing."),
    (c3, "Simple workflow", "Record, upload audio, or paste a supported URL and get your transcript in one place."),
]:
    with col:
        st.markdown(f'<div class="feature"><h3>{title}</h3><p>{text_}</p></div>', unsafe_allow_html=True)

st.markdown('<footer>KraVoice · AI audio transcription by Kraverse</footer>', unsafe_allow_html=True)
