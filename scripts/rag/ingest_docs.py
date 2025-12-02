import re, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

def iter_docs():
    roots = [Path("docs"), Path("README.md")]
    for root in roots:
        if root.is_file():
            text = root.read_text(encoding="utf-8", errors="ignore")
            yield {"title": "README", "url": "", "text": text}
        else:
            for p in root.rglob("*"):
                if p.suffix.lower() in {".md", ".txt"}:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    yield {"title": p.stem, "url": "", "text": text}

def main():
    docs = [d for d in iter_docs()]
    if not docs:
        print("No docs found.")
        return

    corpus = [d["text"] for d in docs]
    vectorizer = TfidfVectorizer(max_features=50000, stop_words="english")
    X = vectorizer.fit_transform(corpus)

    out_dir = Path("models/rag")
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, out_dir/"tfidf_vectorizer.joblib")
    joblib.dump(X, out_dir/"tfidf_matrix.joblib")
    with (out_dir/"docs.jsonl").open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"Indexed {len(docs)} docs → {out_dir}")

if __name__ == "__main__":
    main()
