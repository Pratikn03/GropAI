from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_explain_tabular_handles_missing_model():
    resp = client.get("/explain/tabular")
    assert resp.status_code == 404
    assert "not available" in resp.json()["detail"]
