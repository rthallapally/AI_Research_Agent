# tests/test_gather_web.py

from agent.gather_web import search_duckduckgo

def test_search_duckduckgo():
    results = search_duckduckgo("AI healthcare diagnostics", max_results=3)
    assert isinstance(results, list)
    assert 1 <= len(results) <= 3
    for result in results:
        assert isinstance(result, dict)
        assert "title" in result and "url" in result
        assert isinstance(result["title"], str)
        assert isinstance(result["url"], str)
