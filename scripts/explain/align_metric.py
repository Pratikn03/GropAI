from pathlib import Path
import json

import pandas as pd

SHAP_TOPK = Path("reports/explain/tabular/batch/per_sample_topk.csv")
ALIGN_OUT = Path("reports/explain/align/align_at_k.csv")
ALIGN_OUT.parent.mkdir(parents=True, exist_ok=True)
RAG_DOCS = Path("models/rag/docs.jsonl")


def load_rag_texts():
    if not RAG_DOCS.exists():
        return []
    return [json.loads(line) for line in RAG_DOCS.read_text(encoding="utf-8").splitlines() if line.strip()]


def jaccard(a: str, b: str) -> float:
    A = set(a.lower().split())
    B = set(b.lower().split())
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def main():
    if not SHAP_TOPK.exists():
        print("Missing SHAP topk CSV.")
        return
    rag_docs = load_rag_texts()
    shap_df = pd.read_csv(SHAP_TOPK)
    align_rows = []
    for k in [1, 3, 5]:
        matches = []
        for _, row in shap_df.iterrows():
            tokens = [token for token in str(row.get("topk_feature_idx", "")).split(";") if token]
            top_feat = " ".join(tokens)
            best_score = 0.0
            for doc in rag_docs[:5]:
                best_score = max(best_score, jaccard(top_feat, doc.get("text", "")))
            matches.append(best_score >= 0.1)
        pct = 100.0 * sum(matches) / len(matches) if matches else 0.0
        align_rows.append({"k": k, "align_pct": round(pct, 3)})
    if align_rows:
        pd.DataFrame(align_rows).to_csv(ALIGN_OUT, index=False)
        print("Align@K metric stored ->", ALIGN_OUT)


if __name__ == "__main__":
    main()
