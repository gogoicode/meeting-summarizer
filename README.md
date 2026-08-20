# Meeting Summarizer

> Transcribe meeting audio and generate action-oriented summaries powered by Google Gemini Flash.

Upload a meeting recording to generate an instant **transcript**, **key decisions**, and **action items** — all powered by a single API pipeline.

---

## Features

- **Audio Transcription** — Converts meeting audio directly to plain text using Google Gemini Flash.
- **AI-Powered Summaries** — Generates structured executive summaries from the transcript.
- **Key Decisions Extraction** — Highlights critical decisions made during the meeting.
- **Action Items with Owners** — Identifies tasks and assigns owners/deadlines when mentioned.
- **Meeting History** — Every processed meeting is saved locally and can be revisited from the sidebar.
- **Downloadable Reports** — Export the complete transcript and summary as a `.txt` file.
- **Session-Based Security** — API keys reside in browser memory and are never saved to disk.

---

## Tech Stack

| Component                         | Technology                            |
| :--------------------------------- | :------------------------------------- |
| **Frontend / UI**                  | Streamlit                              |
| **Transcription & Summarization**  | Google Gemini Flash (`google-genai`)   |
| **Storage**                        | SQLite (Python built-in, no extra dependency) |
| **Language**                       | Python 3.10+                           |

---

## Prerequisites

- Python 3.10 or higher
- A [Google Gemini API Key](https://aistudio.google.com/apikey) (free)

---

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/gogoicode/meeting-summarizer.git
   cd meeting-summarizer
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and add your key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   Alternatively, skip this step and paste your key directly into the app's sidebar at runtime — it's kept in-session only and never written to disk.

5. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`.

---

## Project Structure

```text
meeting-summarizer/
├── .streamlit/
│   └── config.toml      # Streamlit toolbar/theme config
├── app.py                # Main Streamlit application
├── database.py            # SQLite storage layer (backend persistence)
├── style.css               # Custom CSS (loaded by app.py via load_css())
├── requirements.txt         # Minimal Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                 # Excludes .env, __pycache__, meetings.db, etc.
└── README.md                   # Project documentation
```

---

## Design Decisions

**Why a single API instead of separate ASR + LLM services?**
Gemini Flash is natively multimodal — it accepts audio directly and can transcribe and reason over it in one call. Rather than chaining a dedicated ASR service (e.g. Whisper) into a second LLM call, this app uses one provider for both stages. This reduces integration complexity, latency, and cost while still meeting every functional requirement: transcript, summary, and action items.

**Why is the API key entered in the UI instead of hardcoded server-side?**
This is a public repository with no dedicated backend or user authentication layer. Hardcoding a personal API key into the source would expose it to anyone who clones the repo. Instead, each user supplies their own free Gemini key at runtime; it lives only in `st.session_state` for that session and is never persisted to disk. This is the standard security pattern for public "bring your own key" tools.

**Why SQLite for storage?**
It's part of Python's standard library — no new dependency is introduced, keeping the project's dependency footprint minimal as required. It's sufficient for a single-user, local-first tool: every processed meeting (filename, timestamp, transcript, summary) is logged and browsable from the sidebar. Note: on ephemeral hosting (e.g. Streamlit Community Cloud), the local database resets on redeploy — this is expected behavior for a local-first storage design, not a bug.

---

## Deliverables

- ✅ GitHub repository (this repo)
- ✅ README with setup, usage, and design rationale
- ✅ Demo video Google Drive [link](https://drive.google.com/file/d/1kiww_WrRzDX58lzvnqYjjgyAz-yKqHlW/view?usp=sharing)
