# tests/test_gather_docs.py

from agent.gather_docs import extract_web_page

def test_extract_web_page():
    # Using a public Wikipedia page as a stable test case
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence_in_healthcare"
    content = extract_web_page(url)
    assert isinstance(content, str)
    assert len(content) > 100  # Should get some real content
