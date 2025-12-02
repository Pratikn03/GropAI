from fastapi import APIRouter, HTTPException

from ..services.rag_index import rag_index

router = APIRouter()


@router.get("/ping")
def ping():
    return {"router": "rag"}


@router.post("/ingest")
def ingest(body: dict):
    docs = body.get("docs")
    if not docs or not isinstance(docs, list):
        raise HTTPException(status_code=400, detail="Provide a list of docs to ingest.")
    stored = rag_index.ingest(docs)
    return {"ingested": len(stored)}


@router.post("/search")
def search(body: dict):
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")
    top_k = int(body.get("top_k", 5))
    hits = rag_index.search(query, top_k)
    return {"hits": hits, "count": len(hits)}
