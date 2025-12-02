from __future__ import annotations

import os

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_tabular_hpo_dry_run():
    os.environ["DRY_RUN"] = "1"
    resp = client.post("/train/tabular/hpo", json={"dataset": "tabular_credit_demo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "dry-run"
    assert body["dataset"] == "tabular_credit_demo"


def test_rag_build_dry_run():
    os.environ["DRY_RUN"] = "1"
    resp = client.post("/train/rag/build", json={"docs": [{"text": "hello"}]})
    assert resp.status_code == 200
    assert resp.json()["status"] == "dry-run"
