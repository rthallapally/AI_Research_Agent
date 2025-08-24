import json
from typing import Dict
from agent.json_formatter import generate_graph_json

def json_generator(state: Dict) -> Dict:
    """
    Inputs from pipeline state:
      - state['query'] (topic)
      - state['final_report'] or state['report'] (text)
    Produces:
      - state['knowledge_graph'] (elements)
      - writes ./data.json for any Streamlit viewer to pick up
    """
    topic = state.get("query", "Knowledge Graph")
    report = state.get("final_report") or state.get("report", "")

    if not report.strip():
        graph = {"nodes": [{"data": {"id": "query", "label": "QUERY", "name": topic}}], "edges": []}
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        return {**state, "knowledge_graph": graph}

    graph = generate_graph_json(report, topic=topic, strict=True, add_degree=True)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    return {**state, "knowledge_graph": graph}
