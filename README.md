## 🤖 AI Research Agent for Healthcare Diagnostics
An intelligent research assistant that autonomously conducts research, gathers information from multiple sources, synthesizes findings with confidence scores, and generates a comprehensive research report — all through an intuitive Streamlit UI.

## 🚀 Features
✅ Multi-step research planning (with sub-questions)
✅ Gathers evidence from:

🌐 Web (DuckDuckGo Search)

📚 Academic papers (arXiv, PubMed)

📄 Local documents (PDF, text)
✅ Uses GROQ LLMs (e.g., LLaMA 3.1) for synthesis
✅ Confidence scores (%) for all findings
✅ Executive summary & citations
✅ Outputs a clean, structured report
✅ Streamlit web interface with real-time progress
✅ Exports reports as .txt
✅ Includes automated tests

## 🛠️ Technology Stack
🧠 LangGraph — State machine to orchestrate the research pipeline

🔗 LangChain — LLM integrations & vectorstore interface

💬 GROQ — Free LLMs (e.g., LLaMA 3.1 8b)

🗄️ Zilliz / Milvus — Scalable vector database for chunk storage & retrieval

🌐 DuckDuckGo Search — Web search

📚 arXiv & PubMed — Academic search

📄 Streamlit — User interface

🧪 Pytest — Testing

## 📋 Project Architecture
less
Copy
Edit
[ User (Streamlit UI) ]
        |
  [ LangGraph Orchestrator ]
        |
----------------------------------------------------
| Planner | Gatherer | Vector Store | Synthesizer |
    ↓         ↓            ↔            ↓
  Sub-qs   Evidence      Stores      Findings +
           Gathering     Chunks     Executive Summary
## 📦 Installation & Setup
1️⃣ Clone the repo

git clone https://github.com/rthallapally/AI_Research_Agent.git
cd AI_Research_Agent

2️⃣ Set up a virtual environment

python -m venv venv
source venv/bin/activate      # On Mac/Linux
venv\Scripts\activate         # On Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Configure environment variables
Create a .env file in the project root:

GROQ_API_KEY="your-groq-api-key"
ZILLIZ_URI="your-zilliz-uri"
ZILLIZ_API_KEY="your-zilliz-api-key"

## 🚀 Running the App
Start the Streamlit UI:

streamlit run app.py

Then open your browser at:
👉 http://localhost:8501

🧪 Running Tests
To run the automated tests:

pytest tests/

## 📜 Example Output
✅ Executive Summary

✅ Findings (one per sub-question)

✅ Citations & references

✅ Confidence scores (in %)

## Sample research question:

What has been the impact of AI on healthcare diagnostics over the past 5 years?

Output:

Executive Summary: (3–4 paragraphs summarizing findings)

Findings:

Area 1: X% confidence

Area 2: Y% confidence
...

References: [1], [2], …

## 📝 Folder Structure
.
├── agent/                # Core pipeline modules
│   ├── planner.py
│   ├── gatherer.py
│   ├── gather_web.py
│   ├── gather_docs.py
│   ├── gather_academic.py
│   ├── synthesizer.py
│   ├── vectorstore.py
│   └── chunker.py
├── docs/                 # Example PDFs
├── tests/                # Unit tests
├── app.py                # Streamlit UI
├── graph.py              # LangGraph pipeline definition
├── requirements.txt
├── README.md
├── LICENSE
└── .env                  # (not committed — secrets)



## 📄 License
This project is licensed under the MIT License.
