import streamlit as st
from graph import build_graph

st.title("📖 AI Research Agent")

query = st.text_input("Enter your research question:")

if st.button("Run Research Agent") and query:
    st.write("⏳ Running research agent...")
    graph = build_graph()
    result = graph.invoke({"query": query})
    st.markdown(result["report"])
    st.download_button("Download Report", result["report"], file_name="report.txt")
