"""CLI wrapper for the feature store toolkit."""

from __future__ import annotations

import argparse

from scripts.features.build_features import build_snapshot
from scripts.features.load_features import load_latest_snapshot


def main():
    parser = argparse.ArgumentParser(description="Feature store CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a new snapshot.")
    build.add_argument(
        "--dataset",
        default="tabular_credit_demo",
        help="Dataset to use for feature creation.",
    )

    load = subparsers.add_parser("load", help="Load the latest snapshot.")

    args = parser.parse_args()

    if args.command == "build":
        path = build_snapshot(args.dataset)
        print(f"Snapshot created: {path}")
    elif args.command == "load":
        df = load_latest_snapshot()
        print(f"Snapshot is {len(df)} rows x {len(df.columns)} cols.")


if __name__ == "__main__":
    main()
