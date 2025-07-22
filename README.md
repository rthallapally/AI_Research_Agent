# AI Research Agent for Healthcare Diagnostics

## Introduction

This project is an **autonomous research agent** designed to answer complex research questions using multi-step planning, multi-source information gathering, and LLM-powered synthesis. It is built for the Generative AI Research Agent Hackathon and specifically targets the topic:

> **Impact of AI on healthcare diagnostics in the last 5 years**

The agent autonomously plans sub-questions, searches the web and academic databases, processes documents, synthesizes findings, provides references, and outputs a well-structured report via a user-friendly Streamlit web app.

---

## Tech Stack

- **Language:** Python 3.9+
- **Core Framework:** [LangGraph](https://github.com/langchain-ai/langgraph)
- **LLM Integration:** [Ollama](https://ollama.com/) (local LLM, e.g., `llama3`)
- **Vector Store:** [ChromaDB](https://docs.trychroma.com/)
- **Web Search:** DuckDuckGo, (optionally Bing & Google/SerpAPI)
- **Academic Sources:** arXiv (via LangChain loader), PubMed API
- **Document Processing:** PyMuPDF, BeautifulSoup, newspaper3k
- **Frontend:** Streamlit
- **Export:** PDF (`fpdf`), Word (`python-docx`), Markdown, Text
- **Testing:** pytest

---

## How to Run

### **1. Install dependencies**

```bash
pip install -r requirements.txt
```

### **2. Set up LLM (Ollama)**

- Download Ollama for your OS.
- Start Ollama and pull the model you want:

```bash
ollama serve
ollama pull llama3
```

### **3. Run the Streamlit app**

```bash
streamlit run ui/app.py
```

### **4. Enter your research question and click "Run Research Agent"**

- Watch progress and intermediate steps live.
- Download the final report in your preferred format.

---

### **Workflow**

```mermaid
flowchart TD
    A[User Input<br>(Streamlit UI)] --> B[LLM Research Planner<br>(Ollama)]
    B --> C1[Web Search<br>(DuckDuckGo, Bing, Google)]
    B --> C2[Academic Search<br>(arXiv, PubMed)]
    B --> C3[Document Processing<br>(PDF, Web, Text)]
    C1 --> D[Chunk & Store<br>(ChromaDB)]
    C2 --> D
    C3 --> D
    D --> E[Semantic Search<br>(Vector Similarity)]
    E --> F[Synthesize Answers<br>(LLM)]
    F --> G[Report Generator<br>(Formatting, Citations)]
    G --> H[UI Output<br>(Show/Export)]
    H --> I{Export Options}
    I --> I1[Download as PDF]
    I --> I2[Download as Word]
    I --> I3[Download as Markdown/Text]
```
