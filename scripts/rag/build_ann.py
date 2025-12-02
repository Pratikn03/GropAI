from pathlib import Path
import json
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


def iter_docs():
    roots = [Path("README.md"), Path("docs")]
    for r in roots:
        if r.is_file():
            yield {"title": "README", "url": "", "text": r.read_text(encoding="utf-8", errors="ignore")}
        elif r.exists():
            for p in r.rglob("*"):
                if p.suffix.lower() in {".md", ".txt"}:
                    yield {"title": p.stem, "url": "", "text": p.read_text(encoding="utf-8", errors="ignore")}


def main():
    docs = [d for d in iter_docs()]
    if not docs:
        print("No docs found.")
        return

    corpus = [d["text"] for d in docs]
    vec = TfidfVectorizer(max_features=100000, stop_words="english")
    X = vec.fit_transform(corpus)
    svd = TruncatedSVD(n_components=256, random_state=42)
    Z = svd.fit_transform(X)
    Z = normalize(Z).astype("float32")

    out = Path("models/rag")
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(vec, out / "tfidf_vectorizer.joblib")
    joblib.dump(svd, out / "svd.joblib")
    np.save(out / "embeddings.npy", Z)
    with (out / "docs.jsonl").open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    have_faiss = False
    try:
        import faiss
        idx = faiss.IndexFlatIP(Z.shape[1])
        idx.add(Z)
        faiss.write_index(idx, str(out / "faiss.index"))
        have_faiss = True
    except Exception:
        pass

    print(f"Indexed {len(docs)} docs → {out} | FAISS={'yes' if have_faiss else 'no'}")


if __name__ == "__main__":
    main()
