# tests/test_chunker.py

from agent.chunker import chunk_text, chunk_documents
from langchain_core.documents import Document

def test_chunk_text():
    text = "AI in healthcare is revolutionizing diagnostics. " * 50  # Long text
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
    assert isinstance(chunks, list)
    assert all(isinstance(c, Document) for c in chunks)
    assert len(chunks) > 1
    for chunk in chunks:
        assert isinstance(chunk.page_content, str)
        assert 50 < len(chunk.page_content) <= 200

def test_chunk_documents():
    docs = [Document(page_content="AI and medicine." * 20)]
    chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=20)
    assert isinstance(chunks, list)
    assert all(isinstance(c, Document) for c in chunks)
    assert len(chunks) > 1
