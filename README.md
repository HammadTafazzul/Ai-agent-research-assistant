# Ai-agent-research-assistant

> Full AI-powered research summarizer web application — submit a query, fetch sources, extract content, generate structured summaries with Google Gemini, and store reports for future reference.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](#requirements)

---

## Table of contents

- [About](#about)
- [How it works (plain words)](#how-it-works-plain-words)
- [Simplified diagram](#simplified-diagram)
- [Where AI is used](#where-ai-is-used)
- [Installation & run](#installation--run)
- [Environment variables](#environment-variables)
- [Project structure & files of interest](#project-structure--files-of-interest)
- [Example results](#example-results)
- [Screenshots & where to add them](#screenshots--where-to-add-them)
- [Error handling & notes](#error-handling--notes)
- [Contributing](#contributing)
- [License](#license)

---

## About

This repository implements a research summarizer web app built with Flask. Users submit a research query; the app scrapes and extracts content from the top web results (HTML or PDF), summarizes the text using Google Gemini, and stores structured reports in SQLite for later review.

---

## How it works (plain words)

1. **User Query** — User enters a query in the web UI.  
2. **Search** — The backend uses SerpAPI to find top 3–5 relevant URLs.  
3. **Extraction** — Each URL is fetched:
   - HTML pages → extracted with `trafilatura`
   - PDFs → extracted with `pypdf`
4. **Summarization** — Extracted text is passed to Google Gemini (via `google-genai` SDK) with a structured JSON prompt. The output includes:
   - `title`, `summary`, `key_points`, `sources`
   - The summarizer can fall back to raw text if parsing fails
5. **Storage** — Reports saved to SQLite (SQLAlchemy) with fields:
   - `query`, `title`, `full_text`, `sources`, `summary_json`, `status`, `notes`
6. **UI** — Users can:
   - Submit queries (`index.html`)
   - Browse report history (`history.html`)
   - View detailed report pages (`report.html`)

---

## Simplified diagram

User Query
│
▼
Flask App
│
├─> SerpAPI → URLs
│
├─> Extractor → Text (HTML / PDF)
│
├─> Gemini Summarizer → Summary JSON
│
└─> SQLite (SQLAlchemy) - Report Storage
│
▼
UI (Submit / View Reports)


> You can replace the ASCII diagram with a nicer image: `assets/architecture.png` (see **Screenshots** section below).

---

## Where AI is used

- **Google Gemini (via `google-genai`)**:
  - Produces structured JSON: `title`, `summary`, `key_points`, `sources`.
  - Handles unexpected outputs safely; the system logs raw AI outputs for debugging and shows a friendly error if the AI fails.

---

## Installation & run

1. **Create & activate venv**
```bash
python -m venv venv
# mac / linux
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```
2. **Install dependencies**
```bash
pip install -r requirements.txt
```
3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env to add:
# SERPAPI_KEY=your_serpapi_key
# GEMINI_API_KEY=your_gemini_key
# FLASK_SECRET=your_flask_secret
```
4. **Run the app**
```bash
python app.py
```
5. **Open in browser**
```bash
http://127.0.0.1:5000
```

## Environment Variables

Create a `.env` file in the project root (do not commit `.env` to git). Add the following variables:

- `SERPAPI_KEY` — SerpAPI key for web search  
- `GEMINI_API_KEY` — Google Gemini / google-genai API key  
- `FLASK_SECRET` — Flask secret key  
- *(Optional)* `DATABASE_URL` — Override SQLite URL

## Project structure & files of interest
```bash
.
├── app.py                      # Flask routes & main app
├── requirements.txt
├── .env.example
├── extractor/
│   └── extractor.py            # HTML / PDF extraction logic (trafilatura, pypdf)
├── search/
│   └── search_client.py        # SerpAPI wrapper
├── llm/
│   └── summarizer.py           # Google Gemini integration & JSON parsing
├── db/
│   └── models.py               # SQLAlchemy models (Report)
├── templates/
│   ├── index.html
│   ├── history.html
│   └── report.html
├── static/
│   └── css/, js/, images/
└── README.md
```

Files to Check First

- `app.py` — Main flow orchestration (search → extract → summarize → save)  
- `llm/summarizer.py` — Prompt engineering, JSON output parsing, fallback behavior  
- `extractor/extractor.py` — Text extraction logic and fail-safe handling  

## Example Results

**Sample Query:** Latest research on AI in education  

**Generated Summary (example):**  
Title: Latest Research on AI in Education  
Summary: Artificial intelligence is rapidly transforming education. Tools are classified as reactive, predictive, and generative, serving students, teachers, and institutions. Research emphasizes AI literacy and human-centered design.  

**Key Points:**  
- Categorization of AI tools: reactive, predictive, generative  
- Applications across student, teacher, and institutional levels  
- Ethical & practical considerations: AI literacy, fairness, interpretability  

**Sources:**  
- NEA: AI in Education  
- U.S. Dept of Education Report  
- Stanford AI+Education Summit  

---

## Error Handling & Notes

- If extraction fails (e.g. PDF inaccessible), the app logs a note but continues processing other sources.  
- If the summarizer fails to produce structured JSON, the raw text is saved and a friendly UI message is shown.  
- Do not commit `.env` or any secrets to the repo.  
- Turn off `debug=True` in production.  

## Screenshots

### Architecture diagram
- Filename: assets/architecture.png  
- Where to insert: directly under *Simplified diagram* (replace or supplement the ASCII diagram).  

### Extraction pipeline / flowchart
- Filename: assets/extraction_pipeline.png  
- Where to insert: in the *How it works* section (below extraction bullet).  

### UI - Home / Query page
- Filename: assets/ui_home.png  
- Where to insert: in *UI* or *Example Results* section.  

### UI - History page (reports list)
- Filename: assets/ui_history.png  
- Where to insert: near *UI — Users can view* or *Example Results*.  

### UI - Report detail view
- Filename: assets/ui_report.png  
- Where to insert: near *Example Results* or in *Files of Interest*.  

### Generated summary sample
- Filename: assets/sample_summary.png  
- Where to insert: in *Example Results* section (visual example).  


## Contributing

Contributions welcome — open an issue or submit a PR for bug fixes, improvements, or documentation changes.

## License

MIT License © 2025 Hammad Tafazzul

This project is licensed under the MIT License — see the `LICENSE` file for full details.

SPDX: `MIT`

