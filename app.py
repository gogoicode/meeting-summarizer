"""
Meeting Summarizer
Transcribe meeting audio and generate action-oriented summaries
using OpenAI Whisper (ASR) and Google Gemini (LLM).
"""

import os
import io
import tempfile
from datetime import datetime

import streamlit as st
from openai import OpenAI
from google import genai
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a polished UI
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---------- Google Font ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Main container ---------- */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ---------- Hero header ---------- */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 300;
    }

    /* ---------- Section cards ---------- */
    .section-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border: 1px solid #e8ecf4;
        border-radius: 14px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .section-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---------- Status badges ---------- */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
    }
    .status-info {
        background: #d1ecf1;
        color: #0c5460;
    }

    /* ---------- Sidebar styling ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown label {
        color: #e0e0e0 !important;
    }

    /* ---------- File uploader ---------- */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 1rem;
        background: rgba(102, 126, 234, 0.03);
    }

    /* ---------- Expander styling ---------- */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }

    /* ---------- Step indicators ---------- */
    .step-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .step-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        flex-shrink: 0;
    }
    .step-text {
        font-size: 0.95rem;
        color: #444;
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #aaa;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — API key configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🔑 API Configuration")
    st.markdown(
        "Enter your API keys below. They are stored **only in your "
        "browser session** and never saved to disk."
    )

    openai_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="Required for Whisper transcription. Get one at https://platform.openai.com/api-keys",
    )

    gemini_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Required for summary generation. Get one at https://aistudio.google.com/apikey",
    )

    st.markdown("---")
    st.markdown("### 📖 How It Works")
    steps = [
        ("1", "Upload a meeting audio file"),
        ("2", "Whisper API transcribes the audio"),
        ("3", "Gemini generates a structured summary"),
        ("4", "Download the full report"),
    ]
    for num, text in steps:
        st.markdown(
            f'<div class="step-row">'
            f'<div class="step-number">{num}</div>'
            f'<div class="step-text">{text}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "**Supported formats:** MP3, WAV, M4A, WEBM, OGG\n\n"
        "**Max file size:** 25 MB (Whisper API limit)"
    )

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="hero">'
    "<h1>📋 Meeting Summarizer</h1>"
    "<p>Upload meeting audio → Get transcript, key decisions &amp; action items instantly</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = ["mp3", "wav", "m4a", "webm", "ogg"]
MAX_FILE_SIZE_MB = 25

SUMMARY_PROMPT = """You are an expert meeting analyst. Analyze the following meeting transcript and provide a structured summary.

**Format your response EXACTLY as follows (use these exact headings):**

## 📝 Meeting Summary
Provide a concise 3-5 sentence overview of the meeting covering the main topics discussed.

## 🎯 Key Decisions
List each key decision made during the meeting as a bullet point. If no clear decisions were made, state that.

## ✅ Action Items
List each action item as a bullet point in this format:
- **[Owner/Person if mentioned]**: Task description — *Deadline if mentioned*

If no specific owners are mentioned, list the tasks without owners.
If no action items are identified, state that.

## 💡 Additional Notes
List any other important points, concerns raised, or follow-ups mentioned.

---
**MEETING TRANSCRIPT:**

{transcript}
"""


def transcribe_audio(audio_file, api_key: str) -> str:
    """Send audio to OpenAI Whisper API and return the transcript."""
    client = OpenAI(api_key=api_key)

    # Write uploaded file to a temp file (Whisper API needs a file-like object with a name)
    suffix = f".{audio_file.name.rsplit('.', 1)[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )
        return response
    finally:
        os.unlink(tmp_path)


def generate_summary(transcript: str, api_key: str) -> str:
    """Send transcript to Google Gemini and return a structured summary."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=SUMMARY_PROMPT.format(transcript=transcript),
    )
    return response.text


def build_download_text(transcript: str, summary: str) -> str:
    """Combine transcript and summary into a downloadable report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"{'=' * 60}\n"
        f"  MEETING SUMMARIZER REPORT\n"
        f"  Generated: {now}\n"
        f"{'=' * 60}\n\n"
        f"{'─' * 60}\n"
        f"  TRANSCRIPT\n"
        f"{'─' * 60}\n\n"
        f"{transcript}\n\n"
        f"{'─' * 60}\n"
        f"  SUMMARY & ACTION ITEMS\n"
        f"{'─' * 60}\n\n"
        f"{summary}\n"
    )


# ---------------------------------------------------------------------------
# Main UI — file upload & processing
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="section-card">'
    '<div class="section-title">🎙️ Upload Meeting Audio</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=SUPPORTED_FORMATS,
    help=f"Supported: {', '.join(SUPPORTED_FORMATS).upper()} — Max {MAX_FILE_SIZE_MB} MB",
    label_visibility="collapsed",
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------

if uploaded_file is not None:
    # Validate file size
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(
            f"❌ File too large ({file_size_mb:.1f} MB). "
            f"Whisper API limit is {MAX_FILE_SIZE_MB} MB."
        )
        st.stop()

    # Show file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<span class="status-badge status-info">📁 {uploaded_file.name}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<span class="status-badge status-info">📏 {file_size_mb:.2f} MB</span>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<span class="status-badge status-info">🎵 {uploaded_file.type}</span>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Validate API keys
    if not openai_key:
        st.warning("⚠️ Please enter your **OpenAI API key** in the sidebar to proceed.")
        st.stop()
    if not gemini_key:
        st.warning("⚠️ Please enter your **Google Gemini API key** in the sidebar to proceed.")
        st.stop()

    # Process button
    if st.button("🚀 Transcribe & Summarize", type="primary", use_container_width=True):
        # --- Step 1: Transcription ---
        with st.status("🎧 Transcribing audio with Whisper...", expanded=True) as status:
            try:
                transcript = transcribe_audio(uploaded_file, openai_key)
                st.session_state["transcript"] = transcript
                status.update(
                    label="✅ Transcription complete!", state="complete", expanded=False
                )
            except Exception as e:
                status.update(label="❌ Transcription failed", state="error")
                st.error(f"Whisper API error: {e}")
                st.stop()

        # --- Step 2: Summarization ---
        with st.status("🤖 Generating summary with Gemini...", expanded=True) as status:
            try:
                summary = generate_summary(transcript, gemini_key)
                st.session_state["summary"] = summary
                status.update(
                    label="✅ Summary generated!", state="complete", expanded=False
                )
            except Exception as e:
                status.update(label="❌ Summarization failed", state="error")
                st.error(f"Gemini API error: {e}")
                st.stop()

        st.session_state["processed"] = True
        st.rerun()

# ---------------------------------------------------------------------------
# Display results
# ---------------------------------------------------------------------------

if st.session_state.get("processed"):
    transcript = st.session_state.get("transcript", "")
    summary = st.session_state.get("summary", "")

    st.markdown("---")

    # Transcript section
    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">🎙️ Full Transcript</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View full transcript", expanded=False):
        st.text_area(
            "Transcript",
            transcript,
            height=250,
            label_visibility="collapsed",
            disabled=True,
        )

    word_count = len(transcript.split())
    st.markdown(
        f'<span class="status-badge status-success">✅ {word_count} words transcribed</span>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Summary section
    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">📊 Meeting Summary & Action Items</div>',
        unsafe_allow_html=True,
    )
    st.markdown(summary)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download section
    st.markdown("")
    report_text = build_download_text(transcript, summary)
    st.download_button(
        label="📥 Download Full Report",
        data=report_text,
        file_name=f"meeting_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="footer">'
    "Built with Streamlit • Whisper API • Google Gemini<br>"
    "Meeting Summarizer — Unthinkable Solutions Assignment"
    "</div>",
    unsafe_allow_html=True,
)
