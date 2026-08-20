# 📋 Meeting Summarizer

> Transcribe meeting audio and generate action-oriented summaries powered by Google Gemini 2.0 Flash.

Upload a meeting recording to generate an instant **transcript**, **key decisions**, and **action items** — all powered by a single API pipeline.

---

## ✨ Features

- **Audio Transcription** — Converts meeting audio directly to plain text using Google Gemini 2.0 Flash.
- **AI-Powered Summaries** — Generates structured executive summaries from the transcript[cite: 2, 3].
- **Key Decisions Extraction** — Highlights critical decisions made during the meeting[cite: 2, 3].
- **Action Items with Owners** — Identifies tasks and assigns owners/deadlines when mentioned[cite: 2, 3].
- **Downloadable Reports** — Export the complete transcript and summary as a `.txt` file.
- **Session-Based Security** — API keys reside in browser memory and are never saved to disk.

---

## 🛠️ Tech Stack

| Component                         | Technology                               |
| :-------------------------------- | :--------------------------------------- |
| **Frontend / UI**                 | Streamlit                                |
| **Transcription & Summarization** | Google Gemini 2.0 Flash (`google-genai`) |
| **Language**                      | Python 3.10+                             |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A [Google Gemini API Key](https://aistudio.google.com/apikey)[cite: 3]

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/gogoicode/meeting-summarizer.git](https://github.com/gogoicode/meeting-summarizer.git)
   cd meeting-summarizer
   ```

### Project Structure

meeting-summarizer/
├── app.py # Main Streamlit application
├── requirements.txt # Minimal Python dependencies
├── .env.example # Environment variable template
├── .gitignore # Excluded files (node_modules, .env, build artifacts)
└── README.md # Project documentation
