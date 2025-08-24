# agent/synthesizer.py

import asyncio
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from agent.vectorstore import query_vectorstore

load_dotenv()

llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

async def synthesize_subquestion(subq, vectorstore):
    chunks = query_vectorstore(subq, vectorstore)
    context = "\n\n".join(c.page_content for c in chunks)

    prompt = (
        f"Sub-question: {subq}\n\n"
        f"Context:\n{context}\n\n"
        "Write a clear, concise answer with inline citations as [1], [2], etc., and include confidence scores "
        "for each key claim as percentages (e.g., 85%, 92%) in parentheses. "
        "At the end of the answer, include a References section for the citations used."
    )
    response = llm.invoke(prompt)
    return response.content, {c.metadata.get("source", "") for c in chunks}


async def generate_executive_summary(subquestions, answers):
    findings = "\n\n".join(
        f"Sub-question: {sq}\nAnswer:\n{ans}" for sq, ans in zip(subquestions, answers)
    )

    prompt = (
        "Based on the following findings, write an Executive Summary that concisely "
        "summarizes the key insights, trends, and conclusions. Keep it under 150 words. "
        "Do NOT include a heading like 'Executive Summary' — just write the paragraph."
    )
    response = llm.invoke(f"{findings}\n\n{prompt}")
    return response.content.strip()


async def synthesizer_node(state):
    answers, all_sources = [], set()
    vectorstore = state["vectorstore"]

    for subq in state["subquestions"]:
        answer, sources = await synthesize_subquestion(subq, vectorstore)
        answers.append(answer)
        all_sources.update(sources)

    executive_summary = await generate_executive_summary(state["subquestions"], answers)

    return {**state, "answers": answers, "sources": list(all_sources), "executive_summary": executive_summary}


def output_node(state):
    report = "# Final Report\n\n"

    exec_summary = state["executive_summary"].strip()
    report += "## Executive Summary\n"
    report += exec_summary + "\n\n"

    report += "## Findings\n"
    for i, ans in enumerate(state["answers"], 1):
        report += f"### {i}. {state['subquestions'][i-1]}\n{ans}\n\n"

    return {**state, "report": report}
