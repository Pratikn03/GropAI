"""Simple guardrail that surfaces features leaking the target."""

from __future__ import annotations

import argparse

from scripts.data.dataset_registry import load_tabular


def main(argv=None):
    parser = argparse.ArgumentParser(description="Leakage audit for tabular datasets.")
    parser.add_argument(
        "--dataset",
        default="tabular_credit_demo",
        help="Dataset to analyze for leakage.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Correlation threshold to consider leakage.",
    )
    args = parser.parse_args(argv)

    features, target = load_tabular(args.dataset)
    correlations = features.corrwith(target).dropna()
    flagged = correlations[correlations.abs() >= args.threshold]

    if flagged.empty:
        print("No obvious leakage detected.")
        return

    print("Leakage candidates:")
    for feature, corr in flagged.items():
        print(f" - {feature}: correlation={corr:.3f}")


if __name__ == "__main__":
    main()
