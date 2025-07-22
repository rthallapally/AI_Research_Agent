from langchain_community.document_loaders import PyMuPDFLoader

def extract_pdf(path):
    loader = PyMuPDFLoader(path)
    return loader.load()
