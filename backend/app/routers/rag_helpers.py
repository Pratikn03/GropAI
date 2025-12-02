from pathlib import Path
import json

import joblib
import numpy as np

STATE = {"vectorizer": None, "svd": None, "emb": None, "docs": [], "faiss": None}


def _safe_load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def ensure_index():
    base = Path("models/rag")
    if STATE["vectorizer"] is not None:
        return True
    vec = base / "tfidf_vectorizer.joblib"
    svd = base / "svd.joblib"
    emb = base / "embeddings.npy"
    docs = base / "docs.jsonl"
    if not (vec.exists() and svd.exists() and emb.exists() and docs.exists()):
        return False
    STATE["vectorizer"] = joblib.load(vec)
    STATE["svd"] = joblib.load(svd)
    STATE["emb"] = np.load(emb)
    STATE["docs"] = _safe_load(docs)
    try:
        import faiss

        idx_path = base / "faiss.index"
        if idx_path.exists():
            STATE["faiss"] = faiss.read_index(str(idx_path))
    except Exception:
        STATE["faiss"] = None
    return True


def search(query, top_k=5):
    if not ensure_index():
        return []
    vec = STATE["vectorizer"].transform([query])
    proj = STATE["svd"].transform(vec)
    normed = proj / (np.linalg.norm(proj, axis=1, keepdims=True) + 1e-8)
    if STATE["faiss"] is not None:
        D, I = STATE["faiss"].search(normed.astype("float32"), top_k)
        sims = D[0].tolist()
        idxs = I[0].tolist()
    else:
        sim = (STATE["emb"] @ normed.T).ravel()
        idxs = np.argsort(-sim)[:top_k]
        sims = [float(sim[i]) for i in idxs]
    hits = []
    for rank, idx in enumerate(idxs, start=1):
        if idx < 0 or idx >= len(STATE["docs"]):
            continue
        doc = STATE["docs"][idx]
        hits.append(
            {
                "rank": rank,
                "score": sims[rank - 1] if rank - 1 < len(sims) else 0.0,
                "title": doc.get("title", f"doc_{idx}"),
                "text": doc.get("text", "")[:512],
            }
        )
    return hits
