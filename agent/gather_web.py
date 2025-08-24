import os
import logging
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

# Safety margins under provider caps
MAX_WEB_QUERY = int(os.getenv("MAX_WEB_QUERY_CHARS", "380"))
DEFAULT_MAX_RESULTS = int(os.getenv("WEB_MAX_RESULTS", "3"))

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def _clamp_query(q: str) -> str:
    q = " ".join((q or "").split())  # collapse whitespace
    return q[:MAX_WEB_QUERY]

def search_web(query: str, max_results: int | None = None):
    """
    Search the web using Tavily API.
    Returns: [{'url': str, 'content': str}, ...]
    """
    try:
        limit = max_results or DEFAULT_MAX_RESULTS
        q = _clamp_query(query)
        results = client.search(q, max_results=limit)
        raw_results = results.get("results", [])

        # Flatten + normalize
        flat = []
        for item in raw_results:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)

        return [
            {"url": r.get("url", ""), "content": r.get("content", "")}
            for r in flat
            if isinstance(r, dict)
        ]
    except Exception as e:
        log.warning("[Web Search Error] orig_len=%d used_len=%d : %s", len(query or ""), len(_clamp_query(query)), e)
        return []
