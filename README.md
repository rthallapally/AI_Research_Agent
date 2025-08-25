# AI Research Agent

An end‑to‑end LangGraph‑powered research assistant that plans a topic into sub‑questions, gathers evidence from the web/academia/local PDFs, synthesizes an executive summary with citations, and converts the result into an interactive knowledge graph (nodes/edges) — all inside a clean Streamlit UI.

Highlights: Groq LLaMA models • LangGraph orchestration • Zilliz/Milvus vector DB • HuggingFace embeddings • RAG answers with inline citations • Cytoscape / st‑link‑analysis graph viz • CSV/JSON exports

# ✨ Features

Planner (Groq LLaMA 3.x)

Decomposes a research query into 3–5 precise sub‑questions.

Gatherer (Web + Academic + PDFs)

🌐 Web via Tavily (summaries + optional full‑text fetching)

🎓 arXiv via LangChain community wrappers

📄 Local PDFs via PyMuPDF

Embeds all content with HuggingFace MiniLM and indexes in Zilliz/Milvus

Synthesizer (RAG)

Answers each sub‑question with inline numeric citations ([1], [2])

Adds confidence scores for key claims

Produces a concise Executive Summary

Knowledge Graph Generation

LLM converts the final report into strict JSON (nodes/edges), with robust parsing & schema hygiene

Deduped, capped (≤50 nodes, ≤100 edges), and degree added for sizing

Interactive Visualization (Streamlit)

Cytoscape (with fallbacks) + soft color palettes (Nord Muted, Pastel Fog, Dark Slate)

Filters (min. edge confidence, hide isolates), N‑hop subgraph focus

Downloads: research_report.txt, elements.json, adjacency.json, nodes.csv, edges.csv

# 🚀 Quickstart

1) Clone & install

git clone <YOUR_REPO_URL>

cd AI_Research_Agent

python -m venv venv

# Windows: venv\Scripts\activate

# macOS/Linux:

source venv/bin/activate

pip install -r requirements.txt

2) Environment variables

Create .env (or use Streamlit secrets in deployment):

# .env (example)

GROQ_API_KEY=...

TAVILY_API_KEY=...

ZILLIZ_URI=...

ZILLIZ_API_KEY=...

# Optional KG controls

KG_MODEL=llama-3.3-70b-versatile

KG_TEMPERATURE=0.0

MAX_WEB_QUERY_CHARS=380

WEB_MAX_RESULTS=3


Security: Don’t commit real keys. Keep .env out of git and rotate any exposed keys.

3) Run

streamlit run app.py


Enter a topic (e.g., “Impact of LLMs on medical diagnostics”).

Let the agent plan → gather → synthesize → visualize.

(Optional quick tool)

streamlit run app_link_analysis.py


Paste any summary text → generate a KG JSON → visualize immediately.

# 🧩 Configuration & Tuning

Color themes: Sidebar → Theme (Nord Muted, Pastel Fog, Dark Slate).

Graph filters: Minimum edge confidence, hide isolates, N‑hop focus.

Layouts: Concentric, COSE, Breadth-first, Circle, Grid.

KG size caps: 50 nodes / 100 edges for UI performance (adjust in json_formatter.py).

Embedding model: sentence-transformers/all-MiniLM-L6-v2 (set in gatherer).

Vector DB: Zilliz (Milvus) serverless; switch collection naming or reuse strategy as needed.

# 📤 Exports

Report: research_report.txt

Graph JSON:

elements.json (filtered view for the current UI)

adjacency.json (all nodes/edges as shown in UI)

CSV: nodes.csv, edges.csv (filtered view)
