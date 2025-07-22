from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus
import os

# HuggingFace embedding model — runs locally & free
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

collection_name = "research_agent_collection"

def get_vectorstore():
    return Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={
            "uri": os.getenv("ZILLIZ_URI"),
            "token": os.getenv("ZILLIZ_API_KEY"),
        },
    )

def add_chunks_to_vectorstore(chunks, vectorstore):
    vectorstore.add_documents(chunks)

def query_vectorstore(query, vectorstore, k=4):
    return vectorstore.similarity_search(query, k=k)
