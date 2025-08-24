# 🧠 AI Research Agent

A multi-agent Generative AI system that automates literature reviews, knowledge extraction, and insight generation from academic papers, PDFs, and online sources. Built with LangGraph, FastAPI, Streamlit, and 
Milvus, the agent delivers citation-backed summaries, semantic search, and knowledge graph visualizations to accelerate research.

# 🚀 Features

Multi-Agent Orchestration: Planner → Gatherer → Synthesizer pipeline for structured research automation.

Retrieval-Augmented Generation (RAG): Semantic search across PDFs, academic APIs (arXiv, PubMed), and web sources.

Knowledge Graphs: Extract entities/relationships from research and visualize them interactively.

Citation Tracking: Generates APA-style references with >95% coverage for transparency.

Real-Time Streaming: Token-level response streaming with FastAPI + Streamlit (<200ms latency).

Extensible Architecture: Modular agents, easy to plug in new APIs or vector stores.

# 🛠️ Tech Stack

LLM Orchestration: LangGraph, LangChain, Groq

Vector DBs: Milvus (Zilliz), FAISS

Embeddings: HuggingFace, OpenAI

APIs: arXiv, PubMed, Tavily, DuckDuckGo, YouTube, GitHub

Frontend & Streaming: Streamlit, FastAPI

Visualization: Cytoscape.js, Pyvis


# ⚙️ Setup Instructions

1. Clone Repo
   
git clone https://github.com/rthallapally/AI_Research_Agent.git

cd AI_Research_Agent

3. Create Virtual Environment

python -m venv venv

source venv/bin/activate   # Linux/Mac

venv\Scripts\activate      # Windows

4. Install Dependencies

pip install -r requirements.txt

5. Add Environment Variables

Copy .env.example → .env and add your API keys:

GROQ_API_KEY=your_key_here

ZILLIZ_API_KEY=your_key_here

5. Run the App

streamlit run app/app.py
