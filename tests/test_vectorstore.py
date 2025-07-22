# tests/test_vectorstore.py

from agent.vectorstore import get_vectorstore, add_chunks_to_vectorstore, query_vectorstore
from agent.chunker import chunk_text
from langchain_core.documents import Document

def test_vectorstore_add_and_query():
    # Create small fake chunks
    text = "AI helps detect cancer in radiology images. AI speeds up diagnostics."
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    vs = get_vectorstore(persist_directory="./test_chroma_db")
    add_chunks_to_vectorstore(chunks, vs)
    results = query_vectorstore("AI and cancer detection", vs, k=2)
    assert isinstance(results, list)
    assert all(isinstance(doc, Document) for doc in results)
    # Should find at least one relevant chunk
    assert len(results) >= 1
