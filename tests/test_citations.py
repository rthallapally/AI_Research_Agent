# tests/test_citations.py

from agent.citations import extract_sources_from_chunks, render_citations

class DummyChunk:
    def __init__(self, meta):
        self.metadata = meta

def test_extract_sources_from_chunks():
    chunks = [
        DummyChunk({'source': 'https://arxiv.org/abs/2007.07892'}),
        DummyChunk({'source': 'https://pubmed.ncbi.nlm.nih.gov/123456/'}),
        DummyChunk({'source': 'https://arxiv.org/abs/2007.07892'})  # duplicate
    ]
    sources = extract_sources_from_chunks(chunks)
    assert isinstance(sources, list)
    assert len(sources) == 2  # Should be unique sources
    assert 'https://arxiv.org/abs/2007.07892' in sources
    assert 'https://pubmed.ncbi.nlm.nih.gov/123456/' in sources

def test_render_citations():
    sources = [
        'https://arxiv.org/abs/2007.07892',
        'https://pubmed.ncbi.nlm.nih.gov/123456/'
    ]
    citations = render_citations(sources)
    assert "References" in citations
    assert "[1]:" in citations or "[1]:" in citations  # Accepts either markdown or plain text
    assert sources[0] in citations and sources[1] in citations
