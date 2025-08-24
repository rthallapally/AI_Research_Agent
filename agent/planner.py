# agent/planner.py

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize the LLM (LLaMA 3.1 via GROQ API)
llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def planner_node(state: dict) -> dict:
    """
    Decomposes a research query into 3–5 sub-questions using LLM.
    Input:
        state: {"query": "<main research question>"}
    Output:
        state + {"subquestions": [q1, q2, q3, ...]}
    """
    query = state.get("query", "").strip()

    if not query:
        raise ValueError("Missing 'query' in state.")

    prompt = (
        "Decompose the following research question into 3 to 5 specific, answerable sub-questions:\n\n"
        f"{query}\n\nReturn the list in a numbered format like 1. ..., 2. ..., etc."
    )

    response = llm.invoke(prompt)
    raw_lines = response.content.strip().splitlines()

    # Extract sub-questions from the response
    subqs = [line.split('.', 1)[-1].strip() 
             for line in raw_lines if line and line[0].isdigit()]

    return {
        "query": query,
        "subquestions": subqs
    }
