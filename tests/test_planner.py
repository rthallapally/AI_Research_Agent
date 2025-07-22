# tests/test_planner.py

from agent.planner import generate_subquestions

def test_generate_subquestions():
    question = "Impact of AI on healthcare diagnostics in the last 5 years"
    subqs = generate_subquestions(question)
    assert isinstance(subqs, list)
    assert len(subqs) >= 2  # Should generate at least two sub-questions
    assert all(isinstance(q, str) and q for q in subqs)
