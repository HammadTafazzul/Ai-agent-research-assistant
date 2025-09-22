# app.py
from dotenv import load_dotenv
load_dotenv()   # <<-- MUST run before importing llm.summarizer

import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from db.models import get_session, Report
from search.search_client import serpapi_search
from extractor.extractor import extract_from_url
from llm.summarizer import summarize_with_gemini

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev_secret")
session = get_session()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    query = request.form.get("query", "").strip()
    if not query:
        flash("⚠️ Please enter a query.", "error")
        return redirect(url_for("index"))

    # Search
    try:
        hits = serpapi_search(query, num_results=5)
    except Exception as e:
        logger.error(f"Search error: {e}")
        flash("❌ Search failed. Please try again later.", "error")
        return redirect(url_for("index"))

    # Extract sources
    sources = []
    notes = []
    for hit in hits[:3]:
        url = hit.get("link")
        text, error = extract_from_url(url)
        if error:
            logger.warning(f"Extraction failed for {url}: {error}")
            notes.append(f"{url} skipped: {error}")
            continue
        sources.append({"url": url, "title": hit.get("title"), "excerpt": text[:3000]})

    status = "ok" if sources else "failed"

    # Summarize with Gemini
    try:
        summary = summarize_with_gemini(query, sources) if sources else {}
    except Exception as e:
        logger.error(f"LLM summarizer crashed: {e}")
        summary = {
            "error": "llm_exception",
            "message": "❌ Our summarizer encountered an error. Please try again later.",
            "exception": str(e),
        }
        status = "partial"

    # Store report
    report = Report(
        query=query,
        title=summary.get("title") if isinstance(summary, dict) and "title" in summary else query,
        summary_json=json.dumps(summary, ensure_ascii=False, indent=2),
        sources_json=json.dumps(sources, ensure_ascii=False, indent=2),
        full_text="\n\n".join([s["excerpt"] for s in sources]),
        status=status,
        notes="\n".join(notes) if notes else None,
    )
    session.add(report)
    session.commit()

    return redirect(url_for("view_report", report_id=report.id))

@app.route("/reports")
def reports():
    items = session.query(Report).order_by(Report.created_at.desc()).all()
    return render_template("history.html", reports=items)

@app.route("/report/<int:report_id>")
def view_report(report_id):
    r = session.query(Report).get(report_id)
    if not r:
        flash("❌ Report not found.", "error")
        return redirect(url_for("index"))

    data = r.to_dict()
    # If summarizer failed, pass friendly message
    summary = data.get("summary_json")
    if isinstance(summary, dict) and "error" in summary and "message" in summary:
        flash(summary["message"], "error")

    return render_template("report.html", report=data)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
