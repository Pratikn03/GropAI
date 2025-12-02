from fastapi import APIRouter
from ..services.state import STATE

router = APIRouter()

@router.post("/consent")
def set_consent(body: dict):
    STATE["consent_enabled"] = bool(body.get("enabled", False))
    return {"status": "ok", "enabled": STATE["consent_enabled"]}

@router.get("/consent")
def get_consent():
    return {"enabled": STATE["consent_enabled"]}
