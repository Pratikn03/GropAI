from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

try:  # Optional at runtime but required for richer dataset metadata
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

router = APIRouter(tags=["features"])

ROOT = Path(__file__).resolve().parents[3]
FEATURE_MANIFEST = ROOT / "feature_store" / "manifest.json"
DATASETS_DIR = ROOT / "configs" / "datasets"


def _read_manifest() -> Dict[str, Any]:
    if not FEATURE_MANIFEST.exists():
        return {"version": None, "snapshots": []}
    try:
        data = json.loads(FEATURE_MANIFEST.read_text(encoding="utf-8"))
        data.setdefault("version", data.get("active_version"))
        data.setdefault("snapshots", data.get("versions", {}).get(data.get("version"), []))
        return data
    except json.JSONDecodeError:
        return {"version": None, "snapshots": []}


def _resolve_data_path(path_value: Optional[str]) -> Optional[Path]:
    if not path_value:
        return None
    candidate = Path(path_value)
    return candidate if candidate.is_absolute() else ROOT / path_value


def _best_effort_size_mb(path: Optional[Path]) -> Optional[float]:
    if not path:
        return None
    try:
        return round(path.stat().st_size / (1024 * 1024), 2)
    except OSError:
        return None


def _best_effort_rows(path: Optional[Path]) -> Optional[int]:
    if not path or not path.exists():
        return None
    try:
        import pandas as pd  # type: ignore
    except Exception:  # pragma: no cover
        return None
    try:
        if path.suffix.lower() == ".parquet":
            frame = pd.read_parquet(path)
        else:
            frame = pd.read_csv(path)
        return int(len(frame))
    except Exception:
        return None


@router.get("/info")
def feature_info() -> Dict[str, Any]:
    manifest = _read_manifest()
    active_version = (
        manifest.get("active_version")
        or manifest.get("version")
        or manifest.get("current_version")
    )
    snapshots: List[Dict[str, Any]] = manifest.get("snapshots", [])
    latest_entry: Optional[Dict[str, Any]] = None
    if snapshots:
        latest_entry = max(
            snapshots,
            key=lambda item: (
                item.get("generated_at") or item.get("date") or ""
            ),
        )

    payload: Dict[str, Any] = {"active_version": active_version, "latest": None}
    if latest_entry:
        data_path = _resolve_data_path(latest_entry.get("path"))
        rows = latest_entry.get("rows")
        if rows is None:
            rows = _best_effort_rows(data_path)
        payload["latest"] = {
            "date": latest_entry.get("date"),
            "path": str(data_path) if data_path else latest_entry.get("path"),
            "size_mb": latest_entry.get("size_mb")
            or _best_effort_size_mb(data_path),
            "rows": rows,
        }
    return payload


@router.get("/datasets")
def dataset_registry() -> Dict[str, Any]:
    if not DATASETS_DIR.exists():
        return {"datasets": []}

    datasets: List[Dict[str, Any]] = []
    files = sorted(DATASETS_DIR.glob("*.yml"))
    for cfg_path in files:
        if yaml is None:
            datasets.append(
                {
                    "name": cfg_path.stem,
                    "config_file": str(cfg_path),
                    "error": "PyYAML not installed",
                }
            )
            continue
        try:
            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            datasets.append(
                {
                    "name": cfg.get("name") or cfg_path.stem,
                    "type": cfg.get("type"),
                    "task": cfg.get("task"),
                    "path_hint": cfg.get("csv_path")
                    or cfg.get("root_dir")
                    or cfg.get("images_dir"),
                    "config_file": str(cfg_path),
                }
            )
        except Exception as exc:
            datasets.append(
                {
                    "name": cfg_path.stem,
                    "config_file": str(cfg_path),
                    "error": f"failed to parse: {exc}",
                }
            )
    return {"datasets": datasets}
