from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "configs" / "datasets"
TABULAR_FALLBACK = [
    {"age": 25, "income": 50000, "score": 720, "defaulted": 0},
    {"age": 36, "income": 82000, "score": 680, "defaulted": 1},
    {"age": 45, "income": 120000, "score": 710, "defaulted": 0},
    {"age": 52, "income": 54000, "score": 650, "defaulted": 1},
]
TEXT_FALLBACK = [
    {"id": 1, "text": "I love the product", "label": "positive"},
    {"id": 2, "text": "The UI is clunky", "label": "negative"},
]
VISION_FALLBACK = [
    {"image_path": str(ROOT / "data" / "placeholder.png"), "label": "demo"},
]


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / path


def list_datasets() -> list[str]:
    """Return sorted dataset names based on files under configs/datasets."""
    return sorted(p.stem for p in DATASET_DIR.glob("*.yml"))


def get_config(name: str) -> dict:
    """Load a dataset config by name."""
    candidate = DATASET_DIR / f"{name}.yml"
    if not candidate.exists():
        raise FileNotFoundError(f"Dataset config for {name} not found")
    return yaml.safe_load(candidate.read_text(encoding="utf-8"))


def load_tabular(name: str) -> Tuple[pd.DataFrame, pd.Series]:
    cfg = get_config(name)
    if cfg.get("type") != "tabular":
        raise ValueError(f"{name} is not a tabular dataset")
    csv_path = _resolve_path(cfg["csv_path"])
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(TABULAR_FALLBACK)
    target_col = cfg.get("target")
    if target_col not in df.columns:
        raise ValueError(f"target column {target_col} not found in {name}")
    return df.drop(columns=[target_col]), df[target_col]


def load_text(name: str) -> pd.DataFrame:
    cfg = get_config(name)
    if cfg.get("type") != "text":
        raise ValueError(f"{name} is not a text dataset")
    csv_path = _resolve_path(cfg["csv_path"])
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame(TEXT_FALLBACK)
    return df


def load_vision(name: str) -> Iterable[dict]:
    cfg = get_config(name)
    if cfg.get("type") != "vision":
        raise ValueError(f"{name} is not a vision dataset")
    images_dir = _resolve_path(cfg["images_dir"])
    labels_csv = _resolve_path(cfg["labels_csv"])
    if images_dir.exists() and labels_csv.exists():
        df = pd.read_csv(labels_csv)
        for row in df.to_dict(orient="records"):
            filename = row.get("filename")
            yield {
                "image_path": str(images_dir / filename),
                "label": row.get("label"),
                **{k: v for k, v in row.items() if k != "filename"},
            }
    else:
        for doc in VISION_FALLBACK:
            yield doc
