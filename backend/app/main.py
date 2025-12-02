from fastapi import FastAPI
from .routers import (
    audio,
    auth,
    chat,
    explain,
    features,
    metrics,
    privacy,
    rag,
    telemetry,
    train,
    vision,
)

app = FastAPI(title="SocialSense-SLM", version="0.1.0")

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(vision.router, prefix="/vision", tags=["vision"])
app.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(train.router, prefix="/train", tags=["train"])
app.include_router(telemetry.router, prefix="/telemetry", tags=["telemetry"])
app.include_router(features.router, prefix="/features", tags=["features"])
app.include_router(explain.router, prefix="/explain", tags=["explain"])

@app.get("/")
def root():
    return {"ok": True, "message": "SocialSense-SLM API is up"}
