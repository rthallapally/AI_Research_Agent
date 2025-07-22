from graph import build_graph

def test_pipeline():
    graph = build_graph()
    result = graph.invoke({"query": "Impact of AI on healthcare diagnostics"})
    assert "report" in result
