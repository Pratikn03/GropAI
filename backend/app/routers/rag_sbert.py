from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

import joblib
import numpy as np

router = APIRouter(tags=["rag"])

STATE = {"embedding": None, "docs": [], "index": None}


def _load():
    base = Path("models/rag_sbert")
    emb_path = base / "embeddings.npy"
    docs_path = base / "docs.jsonl"
    if not emb_path.exists() or not docs_path.exists():
        return False
    STATE["embedding"] = np.load(emb_path)
    STATE["docs"] = [json.loads(line) for line in docs_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    try:
        import faiss

        idx_path = base / "faiss.index"
        if idx_path.exists():
            STATE["index"] = faiss.read_index(str(idx_path))
    except Exception:
        STATE["index"] = None
    return True


def _ensure_loaded():
    if STATE["embedding"] is not None:
        return True
    return _load()


@router.post("/search")
def search(body: dict):
    query = str(body.get("query", "")).strip()
    top_k = int(body.get("top_k", 5))
    if not query:
        raise HTTPException(status_code=400, detail="query required")
    if not _ensure_loaded():
        raise HTTPException(status_code=404, detail="SBERT index missing")
    model = joblib.load(Path("models/rag_sbert") / "encoder.joblib")
    query_vec = model.encode([query], convert_to_numpy=True)
    if STATE["index"] is not None:
        D, I = STATE["index"].search(query_vec.astype("float32"), top_k)
        scores = D[0].tolist()
        idxs = I[0].tolist()
    else:
        sims = STATE["embedding"] @ query_vec.T
        sims = sims.ravel()
        idxs = np.argsort(-sims)[:top_k]
        scores = [float(sims[i]) for i in idxs]
    hits = []
    for rank, idx in enumerate(idxs, start=1):
        if 0 <= idx < len(STATE["docs"]):
            doc = STATE["docs"][idx]
            hits.append(
                {
                    "rank": rank,
                    "score": scores[rank - 1],
                    "title": doc.get("title", f"doc_{idx}"),
                    "text": doc.get("text", "")[:512],
                }
            )
    return {"hits": hits}
