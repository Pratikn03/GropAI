"""Batch feature importance generator for tabular datasets."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from scripts.data.dataset_registry import load_tabular
import pandas as pd


def write_report(
    dataset: str,
    top_k: int,
    features: pd.DataFrame,
    target: pd.Series,
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    importance = features.corrwith(target).abs().sort_values(ascending=False)
    global_df = importance.reset_index()
    global_df.columns = ["feature", "importance"]
    global_df.to_csv(output_dir / "global_importance.csv", index=False)

    per_sample_records: list[dict[str, float | int]] = []
    for idx, row in features.iterrows():
        abs_scores = row.abs().nlargest(top_k)
        for rank, feature in enumerate(abs_scores.index, start=1):
            per_sample_records.append(
                {
                    "sample_id": idx,
                    "feature": feature,
                    "value": float(row[feature]),
                    "importance": float(abs_scores.loc[feature]),
                    "rank": rank,
                }
            )
    per_sample_df = pd.DataFrame(per_sample_records)
    per_sample_df.to_csv(output_dir / "per_sample_topk.csv", index=False)


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Generate batch SHAP-style summaries.")
    parser.add_argument(
        "--dataset",
        default="tabular_credit_demo",
        help="Dataset name to draw features from.",
    )
    parser.add_argument(
        "--top-k", type=int, default=3, help="Number of top features per sample."
    )
    parser.add_argument(
        "--out",
        default="reports/explain/tabular/batch",
        help="Directory to write the CSV reports.",
    )
    args = parser.parse_args(argv)
    features, target = load_tabular(args.dataset)
    write_report(
        dataset=args.dataset,
        top_k=args.top_k,
        features=features,
        target=target,
        output_dir=Path(args.out),
    )


if __name__ == "__main__":
    main()
