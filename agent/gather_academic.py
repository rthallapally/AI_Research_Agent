import os
import asyncio
import logging
from langchain_community.utilities import ArxivAPIWrapper

log = logging.getLogger(__name__)
arxiv = ArxivAPIWrapper()

MAX_WEB_QUERY = int(os.getenv("MAX_WEB_QUERY_CHARS", "380"))

def _clamp_query(q: str) -> str:
    q = " ".join((q or "").split())
    return q[:MAX_WEB_QUERY]

async def search_academic(query: str, max_results: int = 3):
    """
    Search academic papers (arXiv) asynchronously.
    Returns: [{'url': str, 'content': str}, ...]
    """
    try:
        q = _clamp_query(query)
        loop = asyncio.get_event_loop()
        # ArxivAPIWrapper.run returns a string summary; wrap in executor
        results = await loop.run_in_executor(None, arxiv.run, q)

        # Normalize to list of dicts
        if isinstance(results, str):
            results = [{"url": "arxiv.org", "content": results}]
        elif isinstance(results, dict):
            results = [results]
        elif isinstance(results, list):
            flat = []
            for r in results:
                if isinstance(r, list):
                    flat.extend(r)
                else:
                    flat.append(r)
            results = flat
        else:
            results = []

        out = []
        for r in results:
            if isinstance(r, dict):
                out.append({"url": r.get("url", "arxiv.org"), "content": r.get("content", str(r))})
            else:
                out.append({"url": "arxiv.org", "content": str(r)})
        return out[:max_results]
    except Exception as e:
        log.warning("[Academic Search Error] %s", e)
        return []
