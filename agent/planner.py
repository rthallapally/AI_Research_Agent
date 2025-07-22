from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def planner_node(state):
    query = state["query"]
    prompt = (
        "Decompose the following research question into 3-5 specific, answerable sub-questions:\n\n"
        f"{query}\n\nReturn as a numbered list."
    )
    response = llm.invoke(prompt)
    subqs = [line.split('.', 1)[-1].strip() 
             for line in response.content.splitlines() if line and line[0].isdigit()]
    return {"query": query, "subquestions": subqs}
