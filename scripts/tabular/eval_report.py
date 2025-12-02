"""Generate classification metrics for a tabular dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.metrics import average_precision_score, classification_report, roc_auc_score

from scripts.data.dataset_registry import load_tabular


def main(argv=None):
    parser = argparse.ArgumentParser(description="Tabular evaluation report")
    parser.add_argument(
        "--dataset",
        default="tabular_credit_demo",
        help="Dataset name to evaluate.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold on normalized score for a binary decision.",
    )
    parser.add_argument(
        "--output",
        default="reports/metrics/eval_report.json",
        help="Path to write the JSON summary.",
    )
    args = parser.parse_args(argv)

    features, target = load_tabular(args.dataset)
    score_feature = features.columns[features.columns.str.contains("score", case=False)]
    if len(score_feature):
        probs = features[score_feature[0]].astype(float)
    else:
        probs = features.mean(axis=1).astype(float)
    probs = (probs - probs.min()) / (probs.max() - probs.min() + 1e-8)
    preds = (probs >= args.threshold).astype(int)

    report = classification_report(target.astype(int), preds, output_dict=True, zero_division=0)
    summary = {
        "roc_auc": float(roc_auc_score(target.astype(int), probs)),
        "pr_auc": float(average_precision_score(target.astype(int), probs)),
        "classification_report": report,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote evaluation report to {output_path}")


if __name__ == "__main__":
    main()
