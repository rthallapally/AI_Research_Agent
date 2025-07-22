# tests/test_gather_academic.py

from agent.gather_academic import search_arxiv, get_pubmed_abstracts

def test_search_arxiv():
    docs = search_arxiv("AI healthcare diagnostics", max_results=2)
    assert isinstance(docs, list)
    assert len(docs) >= 1
    for doc in docs:
        assert hasattr(doc, "page_content")
        assert isinstance(doc.page_content, str)
        assert len(doc.page_content) > 0

def test_get_pubmed_abstracts():
    abstracts = get_pubmed_abstracts("AI healthcare diagnostics", max_results=2)
    assert isinstance(abstracts, list)
    assert len(abstracts) >= 1
    for ab in abstracts:
        assert isinstance(ab, dict)
        assert "title" in ab and "abstract" in ab
        assert isinstance(ab["title"], str)
        assert isinstance(ab["abstract"], str)
        assert len(ab["abstract"]) > 0
