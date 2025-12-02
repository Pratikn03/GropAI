import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.main import app

client = TestClient(app)


def test_train_tabular_hpo():
    response = client.post("/train/tabular/hpo", json={"dataset": "demo"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "Tabular HPO task is not configured" in body["message"]


def test_train_rag_build():
    docs = [{"text": "hello world", "title": "doc1"}]
    response = client.post("/train/rag/build", json={"docs": docs})
    assert response.status_code == 200
    assert response.json()["ingested"] == len(docs)


def test_rag_search_after_ingest():
    docs = [
        {"text": "the quick brown fox", "title": "fox"},
        {"text": "lazy dog sleeping", "title": "dog"},
    ]
    ingest_resp = client.post("/rag/ingest", json={"docs": docs})
    assert ingest_resp.status_code == 200
    search_resp = client.post("/rag/search", json={"query": "fox"})
    assert search_resp.status_code == 200
    payload = search_resp.json()
    assert payload["count"] >= 1
    assert all("doc" in hit for hit in payload["hits"])


def test_explain_tabular_not_ready():
    response = client.get("/explain/tabular")
    assert response.status_code == 404
    assert "Tabular model not available" in response.json()["detail"]
