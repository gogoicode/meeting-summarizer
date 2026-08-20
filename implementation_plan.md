# Meeting Summarizer — Implementation Plan

## Background

**Assignment**: Build a Meeting Summarizer that transcribes meeting audio and generates action-oriented summaries.

**Requirements from the PDFs**:
- **Input**: Meeting audio files (upload via frontend)
- **Output**: Text transcript + summary + action items
- **Tech**: ASR API (OpenAI Whisper) + LLM (Google Gemini) for summarization
- **Deliverables**: GitHub repo (public, `main` branch) + README + demo video
- **Evaluation**: Transcription accuracy, summary quality, LLM prompt effectiveness, code structure

**Current state**: The repo at `https://github.com/gogoicode/meeting-summarizer` only contains the two assignment PDF files. No app code exists yet.

---

## Proposed Changes

### Project Scaffolding

#### [NEW] `.gitignore`
Standard Python gitignore — excludes `__pycache__`, `.env`, `venv/`, `*.pyc`, uploaded audio files, etc.

#### [NEW] `requirements.txt`
Minimal dependencies (per submission guidelines — no extras):
- `streamlit` — Frontend UI
- `openai` — Whisper ASR transcription
- `google-generativeai` — Gemini LLM for summarization
- `python-dotenv` — Load API keys from `.env` locally

#### [NEW] `.env.example`
Template showing the two required API keys (not the actual `.env`):
```
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_gemini_key_here
```

---

### Core Application

#### [NEW] `app.py`
The single-file Streamlit application with this flow:

1. **Sidebar** — API key input fields (users paste their own keys; keys are stored only in session state, never logged)
2. **Audio Upload** — `st.file_uploader` accepting `.mp3`, `.wav`, `.m4a`, `.webm`, `.ogg`
3. **Transcription** — Sends the uploaded audio to **OpenAI Whisper API** (`whisper-1` model) and displays the raw transcript
4. **Summarization** — Sends the transcript to **Google Gemini** (`gemini-2.0-flash`) with a structured prompt:
   > *"Summarize this meeting transcript. Provide: 1) A concise summary, 2) Key decisions made, 3) Action items with owners (if mentioned)."*
5. **Display** — Shows three expandable sections: Transcript, Summary, and Action Items
6. **Download** — Button to download the full output as a `.txt` file

**Design**: Clean, professional Streamlit layout with custom CSS for a polished look. A single `app.py` keeps the project simple per submission guidelines.

---

### Documentation

#### [NEW] `README.md`
Professional README covering:
- Project title & description
- Features list
- Tech stack
- Setup instructions (clone, install, add keys, run)
- Usage guide with screenshots placeholder
- Demo video link placeholder (to be filled after recording)
- Project structure diagram

---

### Cleanup

#### [DELETE] `Assignment Submission Usage Guidelines (4) (3) (1) (2) (1) (1).pdf`
#### [DELETE] `Meeting summarizer (2).pdf`
These are assignment brief files — they should **not** be in the submitted repo per the guidelines ("Submit only the basic application with all required assignment and project code files").

---

## User Review Required

> [!IMPORTANT]
> **API Keys Needed**: You will need two free-tier API keys:
> 1. **OpenAI API key** — for Whisper transcription ([platform.openai.com](https://platform.openai.com))
> 2. **Google Gemini API key** — for summary generation ([aistudio.google.com](https://aistudio.google.com))
>
> The app lets users enter these keys in the sidebar at runtime (they are never committed to code).

> [!WARNING]
> **PDF Deletion**: I will remove the two assignment PDF files from the Git history and repo. The submission guidelines explicitly say to include only project code files. Confirm you're OK with this.

## Open Questions

1. **Do you already have OpenAI and Google Gemini API keys**, or do you need guidance on obtaining them?
2. **Should I delete the PDFs from the repo** as recommended by the submission guidelines, or keep them?

---

## Verification Plan

### Automated Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Verify the app starts without errors
streamlit run app.py --server.headless true
```

### Manual Verification
- Upload a sample audio file → verify transcript appears
- Verify summary + action items are generated correctly
- Verify download button produces a clean `.txt` file
- Verify `.gitignore` excludes `.env` and other unwanted files
- Verify the GitHub repo is clean (no PDFs, no secrets)
