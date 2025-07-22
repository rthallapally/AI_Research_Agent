# tests/test_synthesis_and_citations.py

from agent.synthesizer import synthesize_answer, generate_report
from agent.citations import extract_sources_from_chunks, render_citations
from langchain_core.documents import Document

def test_synthesize_answer():
    subquestion = "How does AI improve diagnostic accuracy?"
    # Create a fake chunk with a known content and fake source
    chunk = Document(page_content="AI models have increased diagnostic accuracy in radiology [source].", metadata={'source': 'https://arxiv.org/abs/2007.07892'})
    answer = synthesize_answer(subquestion, [chunk])
    assert isinstance(answer, str)
    assert len(answer) > 20
    # Should reference source in some way
    assert "[source" in answer or "source" in answer

def test_generate_report_and_citations():
    subqs = ["How does AI help doctors?", "What is the evidence?"]
    answers = ["AI assists by interpreting images [1].", "Studies show accuracy is improved [2]."]
    report = generate_report(subqs, answers)
    assert isinstance(report, str)
    assert "Executive Summary" in report

    # Citations test
    chunk1 = Document(page_content="...", metadata={'source': 'https://arxiv.org/abs/2007.07892'})
    chunk2 = Document(page_content="...", metadata={'source': 'https://pubmed.ncbi.nlm.nih.gov/12345/'})
    sources = extract_sources_from_chunks([chunk1, chunk2])
    refs = render_citations(sources)
    assert "[1]:" in refs or "[1]:" in refs or "References" in refs

