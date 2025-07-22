from agent.gather_web import search_web, extract_web_page
from agent.gather_academic import search_arxiv, get_pubmed_abstracts
from agent.gather_docs import extract_pdf
from agent.chunker import chunk_text, chunk_documents
from agent.vectorstore import get_vectorstore, add_chunks_to_vectorstore
import os

def gatherer_node(state):
    vectorstore = get_vectorstore()
    all_chunks = []

    for subq in state["subquestions"]:
        # Web
        urls = search_web(subq)
        for url in urls:
            page = extract_web_page(url)
            if page:
                all_chunks.extend(chunk_text(page))

        # Academic
        all_chunks.extend(search_arxiv(subq))
        for doc in get_pubmed_abstracts(subq):
            from langchain_core.documents import Document
            all_chunks.append(Document(page_content=doc["abstract"], metadata={"source": doc["title"]}))

    # PDFs
    for file in os.listdir("docs"):
        if file.endswith(".pdf"):
            pdf_chunks = chunk_documents(extract_pdf(f"docs/{file}"))
            all_chunks.extend(pdf_chunks)

    add_chunks_to_vectorstore(all_chunks, vectorstore)

    return {**state, "vectorstore": vectorstore}
