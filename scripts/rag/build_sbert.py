from pathlib import Path

import json
import numpy as np
import joblib

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None


def iter_docs():
    roots = [Path("docs"), Path("README.md")]
    for root in roots:
        if root.is_file():
            yield {"title": "README", "url": "", "text": root.read_text(encoding="utf-8", errors="ignore")}
        else:
            for path in sorted(root.rglob("*.md")) + sorted(root.rglob("*.txt")):
                if path.is_file():
                    yield {"title": path.stem, "url": "", "text": path.read_text(encoding="utf-8", errors="ignore")}


def main():
    if SentenceTransformer is None:
        raise SystemExit("Install sentence-transformers to build SBERT embeddings.")
    docs = list(iter_docs())
    if not docs:
        raise SystemExit("No docs found to index.")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [doc["text"] for doc in docs]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    out_dir = Path("models/rag_sbert")
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "embeddings.npy", embeddings.astype("float32"))
    joblib.dump(model, out_dir / "encoder.joblib")
    with (out_dir / "docs.jsonl").open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    try:
        import faiss

        idx = faiss.IndexFlatIP(embeddings.shape[1])
        idx.add(embeddings.astype("float32"))
        faiss.write_index(idx, str(out_dir / "faiss.index"))
    except Exception:
        pass
    print("SBERT index stored at", out_dir)


if __name__ == "__main__":
    main()
