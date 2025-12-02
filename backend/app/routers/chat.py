from fastapi import APIRouter
from pathlib import Path

from ..services.rag_index import rag_index

router = APIRouter()

MODELS_DIR = Path("models/rag")
rag_index.load_from_artifacts(MODELS_DIR)


def _extractive_answer(query: str, hits: list[dict]) -> str:
    if not hits:
        return "I don't have enough evidence in my local docs to answer that."
    first = hits[0]["doc"]
    text = first.get("text", "")
    similar = first.get("title", f"doc_{hits[0]['rank']}")
    return f"{text[:512]} (source: {similar})"


@router.post("/ask")
def ask(body: dict):
    query = body.get("query", "").strip()
    if not query:
        return {"answer": "", "citations": [], "confidence": 0.0, "refused": True}
    top_k = int(body.get("top_k", 5))
    hits = rag_index.search(query, top_k)
    refused = not hits or (hits and hits[0]["score"] < 0.05)
    answer = _extractive_answer(query, hits) if not refused else "Sorry, I don't have enough evidence in my knowledge base."
    citations = [
        {"title": hit["doc"].get("title", f"doc_{hit['rank']}"), "score": hit["score"]}
        for hit in hits
    ]
    confidence = hits[0]["score"] if hits else 0.0
    return {
        "answer": answer,
        "citations": citations,
        "confidence": float(confidence),
        "refused": refused,
    }
