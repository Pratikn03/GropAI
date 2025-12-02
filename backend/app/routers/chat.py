from fastapi import APIRouter
from .rag_helpers import search as ann_search, ensure_index

router = APIRouter()


@router.post("/ask")
def ask(body: dict):
    query = body.get("query", "").strip()
    if not query:
        return {"answer": "", "citations": [], "confidence": 0.0, "refused": True}
    top_k = int(body.get("top_k", 5))
    ensure_index()
    hits = ann_search(query, top_k)
    if not hits:
        return {"answer": "I don't have enough evidence in my knowledge base.", "citations": [], "confidence": 0.0, "refused": True}
    answer = "\n\n".join(f"[{hit['title']}] {hit['text']}" for hit in hits)
    citations = [{"title": hit["title"], "score": hit["score"]} for hit in hits]
    return {
        "answer": answer,
        "citations": citations,
        "confidence": hits[0]["score"],
        "refused": False,
    }
