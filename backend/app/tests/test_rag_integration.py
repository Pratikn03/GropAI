from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.rag_index import rag_index

client = TestClient(app)


def test_rag_ingest_and_search():
    rag_index.ingest([])
    docs = [
        {"id": "1", "text": "SocialSense data platform is interesting."},
        {"id": "2", "text": "The quick brown fox jumps over the lazy dog."},
    ]
    resp = client.post("/rag/ingest", json={"docs": docs})
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 2

    search_resp = client.post("/rag/search", json={"query": "brown fox"})
    assert search_resp.status_code == 200
    payload = search_resp.json()
    assert payload["count"] >= 1
    assert payload["hits"][0]["doc"]["text"].startswith("The quick brown")
