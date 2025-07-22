# agent/chunker.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_text(text, chunk_size=500, chunk_overlap=100):
    """
    Splits a string of text into overlapping chunks.
    Returns a list of LangChain Document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = splitter.split_documents([Document(page_content=text)])
    return docs

def chunk_documents(documents, chunk_size=500, chunk_overlap=100):
    """
    Splits a list of LangChain Document objects into smaller chunks.
    Returns a flat list of new Document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    all_chunks = []
    for doc in documents:
        all_chunks.extend(splitter.split_documents([doc]))
    return all_chunks

# # Example usage
# if __name__ == "__main__":
#     text = "Artificial intelligence (AI) is transforming healthcare diagnostics. " * 50
#     chunks = chunk_text(text)
#     print(f"Total chunks: {len(chunks)}")
#     for i, chunk in enumerate(chunks[:2]):
#         print(f"\nChunk {i+1}:\n", chunk.page_content[:200])
