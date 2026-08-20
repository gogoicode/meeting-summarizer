"""
Meeting Summarizer
Transcribe meeting audio and generate action-oriented summaries
using Google Gemini for both transcription and summarization.
"""

import os
import tempfile
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
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
    /* ---------- Fonts ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,500;0,600;1,400&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --ink: #111111;
        --ink-soft: #4a4a4a;
        --ink-faint: #8a8a8a;
        --line: #d9d9d9;
        --line-soft: #ececec;
        --paper: #ffffff;
        --paper-tint: #fafafa;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--ink);
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 880px;
    }

    /* ---------- Masthead ---------- */
    .masthead {
        border-bottom: 1px solid var(--ink);
        padding-bottom: 1.4rem;
        margin-bottom: 2.2rem;
    }
    .masthead .eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--ink-faint);
        margin: 0 0 0.6rem 0;
    }
    .masthead h1 {
        font-family: 'Newsreader', serif;
        font-weight: 600;
        font-size: 2.6rem;
        line-height: 1.05;
        letter-spacing: -0.01em;
        margin: 0 0 0.5rem 0;
        color: var(--ink);
    }
    .masthead p {
        font-size: 1rem;
        color: var(--ink-soft);
        margin: 0;
        font-weight: 400;
        max-width: 46ch;
    }

    /* ---------- Section blocks (hairline, no shadow) ---------- */
    .section-card {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 2px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
    }

    .section-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--ink);
        margin-bottom: 1.1rem;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid var(--line-soft);
    }

    /* ---------- Status tags (monochrome, no pill fill) ---------- */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0;
        margin-right: 1.4rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: var(--ink-soft);
        border-bottom: 1px solid var(--line);
    }
    .status-success {
        color: var(--ink);
        font-weight: 500;
    }
    .status-info {
        color: var(--ink-soft);
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: var(--paper-tint);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-weight: 500;
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown label {
        color: var(--ink-soft) !important;
        font-size: 0.85rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: var(--line-soft);
    }
    [data-testid="stSidebar"] input {
        background: #ffffff !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 2px !important;
    }

    /* ---------- File uploader ---------- */
    [data-testid="stFileUploader"] {
        border: 1px dashed var(--line);
        border-radius: 2px;
        padding: 1rem;
        background: var(--paper-tint);
    }
    [data-testid="stFileUploader"] section {
        background: transparent;
    }

    /* ---------- Buttons ---------- */
    .stButton button, .stDownloadButton button {
        background: var(--ink) !important;
        color: #ffffff !important;
        border: 1px solid var(--ink) !important;
        border-radius: 2px !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
    }
    .stButton button:hover, .stDownloadButton button:hover {
        background: #ffffff !important;
        color: var(--ink) !important;
    }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 0.9rem;
        border-radius: 2px !important;
    }

    /* ---------- Step indicators (numbered, no color) ---------- */
    .step-row {
        display: flex;
        align-items: baseline;
        gap: 0.7rem;
        margin-bottom: 0.7rem;
    }
    .step-number {
        font-family: 'JetBrains Mono', monospace;
        color: var(--ink-faint);
        font-size: 0.8rem;
        flex-shrink: 0;
        width: 1.2rem;
    }
    .step-text {
        font-size: 0.85rem;
        color: var(--ink-soft);
    }

    /* ---------- Divider ---------- */
    hr {
        border-color: var(--line-soft);
    }

    /* ---------- Running/buffering indicator: plain spinning circle ---------- */
    [data-testid="stStatusWidget"] svg,
    div[data-testid="stStatusWidget"] > div > svg {
        display: none !important;
    }
    [data-testid="stStatusWidget"]::before {
        content: "";
        display: inline-block;
        width: 15px;
        height: 15px;
        border: 2px solid var(--line);
        border-top-color: var(--ink);
        border-radius: 50%;
        animation: spin 0.75s linear infinite;
        margin-right: 0.4rem;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        padding: 2.4rem 0 1rem 0;
        color: var(--ink-faint);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.04em;
        border-top: 1px solid var(--line-soft);
        margin-top: 2rem;
    }
    /* ---------- Hide Streamlit's default toolbar (Deploy button + menu) ---------- */
    #MainMenu,
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    .stAppDeployButton {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — API key configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## API Configuration")
    st.markdown(
        "Enter your Google Gemini API key. It is stored only in your "
        "browser session and never saved to disk."
    )

    gemini_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Required for transcription & summarization. Get one free at https://aistudio.google.com/apikey",
    )

    st.markdown("---")
    st.markdown("## How It Works")
    steps = [
        ("01", "Upload a meeting audio file"),
        ("02", "Gemini transcribes the audio"),
        ("03", "Gemini generates a structured summary"),
        ("04", "Download the full report"),
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
    st.markdown("## Limits")
    st.markdown(
        "Supported formats — MP3, WAV, M4A, WEBM, OGG\n\n"
        "Max file size — 20 MB (Gemini API limit)"
    )

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------

st.markdown(
    '<div class="masthead">'
    '<p class="eyebrow">Audio → Transcript → Summary</p>'
    "<h1>Meeting Summarizer</h1>"
    "<p>Upload a recording to get a full transcript, key decisions, "
    "and action items — generated in one pass.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = ["mp3", "wav", "m4a", "webm", "ogg"]
MAX_FILE_SIZE_MB = 20

# Map file extensions to MIME types for Gemini API
MIME_TYPES = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "webm": "audio/webm",
    "ogg": "audio/ogg",
}

TRANSCRIPTION_PROMPT = (
    "Listen to this audio file carefully and transcribe the entire content "
    "word-for-word. Output ONLY the raw transcript text, with no headings, "
    "labels, timestamps, or formatting. Just the spoken words as plain text."
)

SUMMARY_PROMPT = """You are an expert meeting analyst. Analyze the following meeting transcript and provide a structured summary.

**Format your response EXACTLY as follows (use these exact headings):**

## Meeting Summary
Provide a concise 3-5 sentence overview of the meeting covering the main topics discussed.

## Key Decisions
List each key decision made during the meeting as a bullet point. If no clear decisions were made, state that.

## Action Items
List each action item as a bullet point in this format:
- **[Owner/Person if mentioned]**: Task description — *Deadline if mentioned*

If no specific owners are mentioned, list the tasks without owners.
If no action items are identified, state that.

## Additional Notes
List any other important points, concerns raised, or follow-ups mentioned.

---
**MEETING TRANSCRIPT:**

{transcript}
"""


def transcribe_audio(audio_file, api_key: str) -> str:
    """Send audio to Google Gemini and return the transcript."""
    client = genai.Client(api_key=api_key)

    # Determine MIME type from file extension
    ext = audio_file.name.rsplit(".", 1)[-1].lower()
    mime_type = MIME_TYPES.get(ext, "audio/mpeg")

    # Upload the audio file to Gemini
    suffix = f".{ext}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_file.getvalue())
        tmp_path = tmp.name

    try:
        # Upload file to Gemini File API
        uploaded = client.files.upload(
            file=tmp_path,
            config=types.UploadFileConfig(mime_type=mime_type),
        )

        # Generate transcription using the uploaded audio
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded.uri,
                            mime_type=uploaded.mime_type,
                        ),
                        types.Part.from_text(text=TRANSCRIPTION_PROMPT),
                    ]
                )
            ],
        )
        return response.text
    finally:
        os.unlink(tmp_path)


def generate_summary(transcript: str, api_key: str) -> str:
    """Send transcript to Google Gemini and return a structured summary."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
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
    '<div class="section-title">Upload Meeting Audio</div>',
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
            f"Maximum allowed is {MAX_FILE_SIZE_MB} MB."
        )
        st.stop()

    # Show file info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<span class="status-badge status-info">FILE — {uploaded_file.name}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<span class="status-badge status-info">SIZE — {file_size_mb:.2f} MB</span>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<span class="status-badge status-info">TYPE — {uploaded_file.type}</span>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Validate API key
    if not gemini_key:
        st.warning("Enter your Google Gemini API key in the sidebar to proceed.")
        st.stop()

    # Process button
    if st.button("Transcribe & Summarize", type="primary", use_container_width=True):
        # --- Step 1: Transcription ---
        with st.status("Transcribing audio with Gemini...", expanded=True) as status:
            try:
                transcript = transcribe_audio(uploaded_file, gemini_key)
                st.session_state["transcript"] = transcript
                status.update(
                    label="Transcription complete", state="complete", expanded=False
                )
            except Exception as e:
                status.update(label="Transcription failed", state="error")
                st.error(f"Gemini API error: {e}")
                st.stop()

        # --- Step 2: Summarization ---
        with st.status("Generating summary with Gemini...", expanded=True) as status:
            try:
                summary = generate_summary(transcript, gemini_key)
                st.session_state["summary"] = summary
                status.update(
                    label="Summary generated", state="complete", expanded=False
                )
            except Exception as e:
                status.update(label="Summarization failed", state="error")
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
        '<div class="section-title">Full Transcript</div>',
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
        f'<span class="status-badge status-success">{word_count} WORDS TRANSCRIBED</span>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Summary section
    st.markdown(
        '<div class="section-card">'
        '<div class="section-title">Meeting Summary &amp; Action Items</div>',
        unsafe_allow_html=True,
    )
    st.markdown(summary)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download section
    st.markdown("")
    report_text = build_download_text(transcript, summary)
    st.download_button(
        label="Download Full Report",
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
    "BUILT WITH STREAMLIT &amp; GOOGLE GEMINI<br>"
    "MEETING SUMMARIZER — UNTHINKABLE SOLUTIONS ASSIGNMENT"
    "</div>",
    unsafe_allow_html=True,
)