# graph.py

from langgraph.graph import StateGraph
from typing import TypedDict
from agent.planner import planner_node
from agent.gatherer import gatherer_node
from agent.synthesizer import synthesizer_node, output_node

class ResearchState(TypedDict, total=False):
    query: str
    subquestions: list[str]
    vectorstore: object
    answers: list[str]
    sources: list[str]
    report: str
    executive_summary: str

def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("gatherer", gatherer_node, is_async=True)  # ✅ updated
    graph.add_node("synthesizer", synthesizer_node, is_async=True)  # ✅ updated
    graph.add_node("output", output_node)

    graph.set_entry_point("planner")
    graph.set_finish_point("output")

    graph.add_edge("planner", "gatherer")
    graph.add_edge("gatherer", "synthesizer")
    graph.add_edge("synthesizer", "output")

    return graph.compile(name="ResearchAgent")
