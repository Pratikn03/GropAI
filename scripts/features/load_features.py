"""Load the latest feature store snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

MANIFEST_PATH = Path("feature_store/manifest.json")


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError("Feature store manifest not found.")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_latest_snapshot() -> pd.DataFrame:
    manifest = _load_manifest()
    snapshots = manifest.get("snapshots", [])
    if not snapshots:
        raise ValueError("No snapshots recorded in manifest.")
    latest = max(snapshots, key=lambda s: s.get("generated_at", ""))
    snapshot_path = Path(latest["path"])
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot file missing: {snapshot_path}")
    df = pd.read_parquet(snapshot_path)
    print(f"Loaded {len(df)} rows from {snapshot_path}")
    return df


def main():
    df = load_latest_snapshot()
    print(df.head())


if __name__ == "__main__":
    main()
