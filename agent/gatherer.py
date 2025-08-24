# agent/gatherer.py
import os
import asyncio
from typing import List
from dotenv import load_dotenv
import streamlit as st

from langchain_community.vectorstores import Zilliz
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from agent.gather_docs import load_local_pdfs
from agent.gather_web import search_web
from agent.gather_academic import search_academic

load_dotenv()

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


async def gather_all(subq: str, local_pdfs: List[Document]) -> List[Document]:
    """
    Gathers documents from web, academic, and local PDFs for a single sub-question.
    Returns a list of Document objects.
    """

    st.write(f"🔹 Processing sub-question: {subq}")

    # Async tasks
    st.write("🌐 Searching the web...")
    web_task = asyncio.to_thread(search_web, subq)  # sync → thread

    st.write("🎓 Searching academic papers...")
    academic_task = search_academic(subq)  # already async

    # Wait for tasks to finish
    web_results, academic_results = await asyncio.gather(web_task, academic_task)

    # Ensure we always get lists
    web_results = web_results or []
    academic_results = academic_results or []

    combined_docs = []
    
    # Convert Web results to Documents
    for r in web_results:
        combined_docs.append(Document(
            page_content=r.get("content", ""),
            metadata={"source": r.get("url", "Web")}
        ))
    
    # Convert Academic results to Documents
    for r in academic_results:
        combined_docs.append(Document(
            page_content=r.get("content", ""),
            metadata={"source": r.get("url", "Academic")}
        ))
    
    # Add preloaded local PDFs
    combined_docs.extend(local_pdfs)

    st.write(f"✅ Collected {len(combined_docs)} documents for this sub-question.\n")

    return combined_docs


async def gatherer_node(state):
    """
    Node to gather all documents for all sub-questions and create the Zilliz vectorstore.
    """
    subquestions = state["subquestions"]

    # Load local PDFs only once
    st.write("📄 Loading local PDFs once...")
    local_pdfs = load_local_pdfs()
    st.write(f"📄 Loaded {len(local_pdfs)} local PDF documents.\n")

    all_docs = []

    st.write("📥 Gathering sources for all sub-questions...\n")
    for idx, subq in enumerate(subquestions, 1):
        st.write(f"🔹 Sub-question {idx}/{len(subquestions)}: {subq}")
        docs = await gather_all(subq, local_pdfs)
        all_docs.extend(docs)

    # Create vectorstore with auto_id=True to avoid ID issues
    st.write("🧠 Creating vectorstore in Zilliz...")
    vectorstore = Zilliz.from_documents(
        all_docs,
        embedding=embedding_model,
        collection_name="research_agent_collection",
        connection_args={
            "uri": os.getenv("ZILLIZ_URI"),
            "token": os.getenv("ZILLIZ_API_KEY"),
        },
        auto_id=True  # ✅ Let Zilliz handle IDs automatically
    )

    st.write("✅ Vectorstore successfully created and ready for semantic search!\n")
    return {**state, "vectorstore": vectorstore}
