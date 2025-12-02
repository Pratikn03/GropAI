from __future__ import annotations

import os
from fastapi import APIRouter

from ..services.rag_index import rag_index

router = APIRouter()


@router.get("/ping")
def ping():
    return {"router": "train"}


def _dry_run() -> bool:
    return os.environ.get("DRY_RUN", "").lower() in {"1", "true", "yes"}


@router.post("/tabular/hpo")
def tabular_hpo(body: dict):
    dataset = body.get("dataset", "tabular_credit_demo")
    if _dry_run():
        return {"status": "dry-run", "dataset": dataset}
    return {
        "status": "ok",
        "dataset": dataset,
        "message": "Tabular HPO task is not configured for end-to-end execution.",
    }


@router.post("/rag/build")
def rag_build(body: dict):
    docs = body.get("docs", [])
    dry = _dry_run()
    if dry:
        return {"status": "dry-run", "ingested": 0}
    stored = rag_index.ingest(docs or [])
    return {"status": "ok", "ingested": len(stored)}
