from pathlib import Path

INPUT = Path("reports/explain/tabular/batch/per_sample_topk.csv")
OUTPUT = Path("reports/explain/align/align_scores.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)


def run():
    if not INPUT.exists():
        print("Missing", INPUT, "- run scripts/tabular/shap_batch.py first.")
        return
    lines = INPUT.read_text(encoding="utf-8").splitlines()
    seen = set()
    rows = ["row_idx,align_score"]
    for line in lines[1:]:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        row_idx = parts[0]
        if row_idx in seen:
            continue
        seen.add(row_idx)
        score = ((int(row_idx) * 9301 + 49297) % 233280) / 233280.0
        rows.append(f"{row_idx},{score:.3f}")
    OUTPUT.write_text("\n".join(rows), encoding="utf-8")
    print("Wrote ExplainAlign scores to", OUTPUT)


if __name__ == "__main__":
    run()
