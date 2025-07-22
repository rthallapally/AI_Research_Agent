from langchain_openai import ChatOpenAI
from agent.vectorstore import query_vectorstore
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def synthesize_subquestion(subq, vectorstore):
    """
    Synthesizes an answer for a single sub-question with confidence scores (in %).
    """
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
    answer = response.content

    # collect sources from chunks
    sources = set()
    for c in chunks:
        if c.metadata.get("source"):
            sources.add(c.metadata["source"])

    return answer, sources


def generate_executive_summary(subquestions, answers):
    """
    Uses LLM to synthesize an executive summary of all findings.
    """
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


def synthesizer_node(state):
    """
    Runs synthesis sequentially for all sub-questions and also generates Executive Summary.
    """
    answers, all_sources = [], set()
    vectorstore = state["vectorstore"]

    for subq in state["subquestions"]:
        answer, sources = synthesize_subquestion(subq, vectorstore)
        answers.append(answer)
        all_sources.update(sources)

    # after gathering all answers → generate executive summary
    executive_summary = generate_executive_summary(state["subquestions"], answers)

    return {**state, "answers": answers, "sources": list(all_sources), "executive_summary": executive_summary}


def output_node(state):
    """
    Builds the final report.
    """
    report = "# Final Report\n\n"

    # Executive Summary
    exec_summary = state["executive_summary"].strip()
    report += "## Executive Summary\n"
    report += exec_summary + "\n\n"

    # Findings
    report += "## Findings\n"
    for i, ans in enumerate(state["answers"], 1):
        report += f"### {i}. {state['subquestions'][i-1]}\n{ans}\n\n"

    # References
    #report += "## References\n"
    #for idx, src in enumerate(state["sources"], 1):
     #   report += f"[{idx}] {src}\n"

    return {**state, "report": report}
