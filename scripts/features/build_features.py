"""Build feature store snapshots from tabular datasets."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from scripts.data.dataset_registry import load_tabular

MANIFEST_PATH = Path("feature_store/manifest.json")
FEATURE_DIR = Path("feature_store/features/v1")


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"version": "v1", "snapshots": []}


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build_snapshot(dataset: str) -> Path:
    features, target = load_tabular(dataset)
    snapshot = features.copy()
    snapshot["target"] = target.values
    timestamp = datetime.now(timezone.utc)
    date_dir = FEATURE_DIR / f"date={timestamp.strftime('%Y%m%d')}"
    date_dir.mkdir(parents=True, exist_ok=True)
    out_path = date_dir / "features.parquet"
    snapshot.to_parquet(out_path, index=False)

    manifest = _load_manifest()
    manifest["snapshots"] = [
        s for s in manifest.get("snapshots", []) if s.get("date") != date_dir.name
    ]
    manifest["snapshots"].append(
        {
            "version": manifest.get("version", "v1"),
            "date": date_dir.name,
            "dataset": dataset,
            "path": str(out_path),
            "rows": len(snapshot),
            "generated_at": timestamp.isoformat(),
        }
    )
    _save_manifest(manifest)
    return out_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build features into the feature store.")
    parser.add_argument(
        "--dataset",
        default="tabular_credit_demo",
        help="Tabular dataset to source features from.",
    )
    args = parser.parse_args(argv)
    out_path = build_snapshot(args.dataset)
    print(f"Feature snapshot written to {out_path}")


if __name__ == "__main__":
    main()
