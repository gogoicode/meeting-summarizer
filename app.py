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
# Style configuration
# ---------------------------------------------------------------------------
def load_css(file_path: str):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

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