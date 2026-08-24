import pytest
from app.retrieval import RetrievalService

@pytest.fixture
def service():
    return RetrievalService()

def test_query_returns_results(service):
    results = service.query("What is the return policy?", top_k=2)
    assert len(results) >= 1
    assert results[0]["source_id"] == "return_policy"
    assert results[0]["score"] > 0

def test_query_no_results(service):
    results = service.query("xyzzy nonsense phrase that does not exist", top_k=2, score_threshold=0.9)
    assert len(results) == 0
