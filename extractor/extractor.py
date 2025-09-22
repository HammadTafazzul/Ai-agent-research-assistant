# extractor/extractor.py
import trafilatura, requests
from pypdf import PdfReader
from io import BytesIO

HEADERS = {"User-Agent": "ai-agent-intern/1.0"}

def fetch_url(url, timeout=10):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.content, r.headers.get("Content-Type", "")
    except Exception as e:
        return None, str(e)

def extract_pdf(content_bytes):
    try:
        b = BytesIO(content_bytes)
        reader = PdfReader(b)
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages).strip()
    except Exception:
        return None

def extract_html(content_bytes, url):
    try:
        text = trafilatura.extract(content_bytes.decode("utf-8", errors="ignore"), url=url)
        return text.strip() if text else None
    except Exception:
        return None

def extract_from_url(url):
    content, ctype_or_err = fetch_url(url)
    if content is None:
        return None, f"fetch_error: {ctype_or_err}"
    ctype = (ctype_or_err or "").lower()
    if "application/pdf" in ctype or url.lower().endswith(".pdf"):
        text = extract_pdf(content)
        return (text, None) if text else (None, "pdf_extract_failed")
    else:
        text = extract_html(content, url)
        return (text, None) if text else (None, "html_extract_failed")
