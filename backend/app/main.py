from fastapi import Depends, FastAPI
from .middleware.rate_limit import SimpleRateLimiter
from .routers import (
    audio,
    auth,
    chat,
    explain,
    features,
    governance,
    metrics,
    privacy,
    rag,
    rag_sbert,
    telemetry,
    train,
    vision,
)
from .security.api_key import require_api_key

app = FastAPI(title="SocialSense-SLM", version="0.1.0", dependencies=[Depends(require_api_key)])  # type: ignore

app.add_middleware(SimpleRateLimiter, calls=120, per_seconds=60)
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(vision.router, prefix="/vision", tags=["vision"])
app.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(rag_sbert.router, prefix="/rag/sbert", tags=["rag"])
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(train.router, prefix="/train", tags=["train"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
app.include_router(features.router, prefix="/features", tags=["features"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])
app.include_router(governance.router, prefix="/governance", tags=["governance"])

@app.get("/")
def root():
    return {"ok": True, "message": "SocialSense-SLM API is up"}
