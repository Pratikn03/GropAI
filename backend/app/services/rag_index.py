from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import numpy as np
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer


class RAGIndex:
    def __init__(self) -> None:
        self.docs: list[dict] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None

    def ingest(self, docs: Iterable[dict]) -> List[dict]:
        clean_docs = [doc for doc in docs if doc.get("text")]
        if not clean_docs:
            self.docs = []
            self.vectorizer = None
            self.matrix = None
            return []
        self.docs = clean_docs
        self.vectorizer = TfidfVectorizer(stop_words="english")
        texts = [doc["text"] for doc in clean_docs]
        self.matrix = self.vectorizer.fit_transform(texts)
        return self.docs

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        if not self.vectorizer or self.matrix is None or not self.docs:
            return []
        vector = self.vectorizer.transform([query])
        matrix_array = self.matrix.toarray()
        vector_array = vector.toarray()
        denom = np.linalg.norm(matrix_array, axis=1) * np.linalg.norm(vector_array)
        denom[denom == 0] = 1e-8
        sim = (matrix_array @ vector_array.T).ravel() / denom
        idx = np.argsort(-sim)[:top_k]
        hits = []
        for rank, i in enumerate(idx, start=1):
            doc = self.docs[int(i)]
            hits.append(
                {
                    "rank": rank,
                    "score": float(sim[i]),
                    "doc": doc,
                }
            )
        return hits

    def load_from_artifacts(self, root: Path) -> bool:
        vectorizer_path = root / "tfidf_vectorizer.joblib"
        matrix_path = root / "tfidf_matrix.joblib"
        docs_path = root / "docs.jsonl"
        if not (vectorizer_path.exists() and matrix_path.exists() and docs_path.exists()):
            return False
        self.vectorizer = load(vectorizer_path)
        self.matrix = load(matrix_path)
        self.docs = [
            json.loads(line)
            for line in docs_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return True


rag_index = RAGIndex()
