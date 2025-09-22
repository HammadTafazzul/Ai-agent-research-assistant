# search/search_client.py
import os, requests
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def serpapi_search(query, num_results=5):
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not set in environment")
    url = "https://serpapi.com/search"
    params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": num_results}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link"),
        })
    return results
