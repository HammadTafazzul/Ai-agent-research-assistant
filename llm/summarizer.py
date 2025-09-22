# llm/summarizer.py  (robust logging + safe returns + friendly errors)
import os
import json
import re
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found in environment. Please set it in .env or system env.")

# Explicit client creation
client = genai.Client(api_key=API_KEY)

PROMPT_TEMPLATE = """
You are a concise research assistant. INPUT: a user query and up to 3 source excerpts (with URLs).
REQUIREMENTS:
1) Output EXACTLY ONE valid JSON object ONLY (no leading/trailing text).
2) The JSON must have keys:
   - title (string)
   - summary (string, 3-4 sentences)
   - key_points (array of 3 objects with 'point' and 'detail')
   - sources (array of objects with 'url' and 'note')
3) If you cannot produce the required JSON, return a single JSON object with keys:
   - error (string explaining reason)
   - raw_output (the full text you would have returned)

User Query: "{query}"
Sources:
{sources_data}

Respond ONLY with a single JSON object. No extra text.
"""

def build_sources_text(sources):
    parts = []
    for i, s in enumerate(sources, start=1):
        parts.append(f"SOURCE {i}: {s.get('url')}\nEXCERPT:\n{s.get('excerpt','')[:3000]}\n")
    return "\n\n".join(parts)

def _try_parse_json(text):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None

def summarize_with_gemini(query, sources, model="gemini-2.5-flash"):
    """
    Summarize research sources with Gemini.
    Returns a dict with valid JSON, or a safe error object if Gemini fails.
    """
    prompt = PROMPT_TEMPLATE.format(query=query, sources_data=build_sources_text(sources))

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        raw_text = (response.text or "").strip()
    except Exception as exc:
        err_msg = str(exc)
        logger.error(f"❌ Gemini API call failed: {err_msg}")
        return {
            "error": "gemini_call_exception",
            "message": "We couldn’t reach the AI summarizer right now. Please try again later.",
            "exception": err_msg,
            "raw_output": ""
        }

    # Debug log
    logger.debug("=== GEMINI RAW OUTPUT START ===")
    logger.debug(raw_text)
    logger.debug("=== GEMINI RAW OUTPUT END ===")

    # Try parsing
    parsed = _try_parse_json(raw_text)
    if parsed is not None:
        return parsed

    # Fallback: friendly message if Gemini didn’t return JSON
    return {
        "error": "non_json_output",
        "message": "The AI summarizer gave an unexpected response. Please try again.",
        "raw_output": raw_text
    }
