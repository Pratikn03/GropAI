from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


@router.get("/risk_score")
def risk_score():
    base = Path("reports/metrics")
    leakage = _load_json(base / "leakage_audit.json") or {"issues": []}
    data = _load_json(base / "data_validation.json") or []
    img_list = []
    img_path = base / "image_validation.txt"
    if img_path.exists():
        img_list = [line for line in img_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    score = 0
    for issue in leakage.get("issues", []):
        sev = (issue.get("severity") or "low").lower()
        if sev == "high":
            score += 25
        elif sev == "medium":
            score += 12
        else:
            score += 5
    for entry in data:
        if entry.get("type") == "missing_values":
            score += 8
        if entry.get("type") == "duplicate_rows":
            score += 6
    score += min(10, len(img_list) // 10)
    score = max(0, min(100, score))
    return {
        "risk_score": score,
        "components": {
            "leakage_issues": len(leakage.get("issues", [])),
            "data_issues": len(data),
            "bad_images": len(img_list),
        },
    }
