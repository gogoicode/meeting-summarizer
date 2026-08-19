# 📋 Meeting Summarizer

> Transcribe meeting audio and generate action-oriented summaries powered by AI.

Upload a meeting recording and get an instant **transcript**, **key decisions**, and **action items** — all in one click.

---

## ✨ Features

- **Audio Transcription** — Converts meeting audio to text using OpenAI Whisper API
- **AI-Powered Summaries** — Generates structured summaries with Google Gemini
- **Key Decisions Extraction** — Highlights important decisions made during the meeting
- **Action Items with Owners** — Identifies tasks and assigns owners when mentioned
- **Download Reports** — Export the full transcript and summary as a `.txt` file
- **Secure** — API keys stay in your browser session; nothing is stored on disk

---

## 🛠️ Tech Stack

| Component       | Technology              |
|-----------------|-------------------------|
| Frontend / UI   | Streamlit               |
| Transcription   | OpenAI Whisper API      |
| Summarization   | Google Gemini 2.0 Flash |
| Language        | Python 3.10+            |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys) (for Whisper)
- A [Google Gemini API key](https://aistudio.google.com/apikey) (for summarization)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/gogoicode/meeting-summarizer.git
   cd meeting-summarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (choose one method)

   **Option A — `.env` file (recommended for local dev)**
   ```bash
   cp .env.example .env
   # Edit .env and add your actual keys
   ```

   **Option B — Enter in the app sidebar**
   Just paste your keys into the sidebar when the app launches.

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📖 Usage

1. Enter your OpenAI and Gemini API keys in the sidebar
2. Upload a meeting audio file (MP3, WAV, M4A, WEBM, or OGG — max 25 MB)
3. Click **"Transcribe & Summarize"**
4. View the transcript, summary, key decisions, and action items
5. Download the full report as a text file

---

## 📁 Project Structure

```
meeting-summarizer/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🎥 Demo

> _Demo video link will be added here after recording._

---

## 📄 License

This project is open-source and available for educational purposes.

---

Built for the **Unthinkable Solutions** assignment.
