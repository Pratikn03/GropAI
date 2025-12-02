from fastapi import APIRouter
from pathlib import Path
import json, re
import joblib
import numpy as np

router = APIRouter()

# Minimal TF-IDF retrieval (no external deps)
_RAG = {"vectorizer": None, "matrix": None, "docs": []}

def _load_rag():
    vec_p = Path("models/rag/tfidf_vectorizer.joblib")
    mat_p = Path("models/rag/tfidf_matrix.joblib")
    docs_p = Path("models/rag/docs.jsonl")
    if vec_p.exists() and mat_p.exists() and docs_p.exists():
        _RAG["vectorizer"] = joblib.load(vec_p)
        _RAG["matrix"] = joblib.load(mat_p)
        _RAG["docs"] = [json.loads(line) for line in docs_p.read_text(encoding="utf-8").splitlines() if line.strip()]
        return True
    return False

def _search(q: str, k: int = 5):
    if _RAG["vectorizer"] is None and not _load_rag():
        return []
    v = _RAG["vectorizer"].transform([q])   # (1, V)
    M = _RAG["matrix"]                       # (N, V)
    # cosine similarity
    denom = np.linalg.norm(M.toarray(), axis=1) * np.linalg.norm(v.toarray())
    denom[denom==0] = 1e-8
    sim = (M @ v.T).toarray().ravel() / denom
    idx = np.argsort(-sim)[:k]
    out = []
    for i in idx:
        d = _RAG["docs"][int(i)]
        out.append({"title": d.get("title", f"doc_{i}"), "url": d.get("url",""), "score": float(sim[i]), "text": d.get("text","")})
    return out

def _extractive_answer(query: str, hits: list[dict]) -> str:
    if not hits:
        return "I don't have enough evidence in my local docs to answer that."
    text = "\n".join(h["text"][:2000] for h in hits if h.get("text"))
    # naive snippet return
    return f"{hits[0]['text'][:512]}"

@router.post("/ask")
def ask(body: dict):
    q = body.get("query","").strip()
    k = int(body.get("top_k", 5))
    hits = _search(q, k=k)
    refused = len(hits) == 0 or (hits and hits[0]["score"] < 0.05)
    answer = _extractive_answer(q, hits) if not refused else "Sorry, I don't have enough evidence in my knowledge base."
    citations = [{"title": h["title"], "url": h["url"], "score": h["score"]} for h in hits]
    return {"answer": answer, "citations": citations, "confidence": (hits[0]["score"] if hits else 0.0), "refused": refused}
