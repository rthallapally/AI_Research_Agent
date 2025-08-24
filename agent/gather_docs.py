# agent/gather_docs.py

import os
from langchain_community.document_loaders import PyMuPDFLoader

def load_local_pdfs(directory: str = "./docs") -> list:
    """
    Loads all PDFs from the given directory into a list of LangChain Document objects.
    """
    docs = []
    if not os.path.exists(directory):
        return docs

    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(directory, filename)
            loader = PyMuPDFLoader(path)
            docs.extend(loader.load())
    return docs

def extract_pdf(path: str) -> list:
    """
    Loads a single PDF file and returns a list of LangChain Document objects.
    """
    if not os.path.exists(path):
        return []
    loader = PyMuPDFLoader(path)
    return loader.load()
