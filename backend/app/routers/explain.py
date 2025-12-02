from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter()


@router.get("/ping")
def ping():
    return {"router": "explain"}


MODEL_PATH = Path("models/tabular/lightgbm_hpo/model_full.joblib")


@router.get("/tabular")
def explain_tabular():
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=404, detail="Tabular model not available for explanations."
        )
    return {"status": "ready", "model_path": str(MODEL_PATH)}
