# agent/vectorstore.py

def query_vectorstore(query, vectorstore, k=4):
    return vectorstore.similarity_search(query, k=k)
