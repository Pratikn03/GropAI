from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import base64
import numpy as np

from ..services.state import STATE
from ..services.vision_infer import VisionONNXService
from ..services.blur import detect_faces_bgr, blur_faces_bboxes

try:
    import cv2
except ImportError:
    cv2 = None

router = APIRouter()

# Lazy singletons
_MODEL: VisionONNXService | None = None

def _get_model() -> VisionONNXService:
    global _MODEL
    if _MODEL is None:
        onnx_path = Path("models/vision/resnet18/model.onnx")
        labels_txt = Path("models/vision/resnet18/labels.txt")
        _MODEL = VisionONNXService(str(onnx_path), str(labels_txt) if labels_txt.exists() else None)
    return _MODEL

def _b64_png(img_bgr: np.ndarray) -> str:
    if cv2 is None:
        return ""
    ok, buf = cv2.imencode(".png", img_bgr)
    return base64.b64encode(buf).decode("ascii") if ok else ""

@router.post("/infer")
async def infer(image: UploadFile = File(...), return_image: bool = Form(False)):
    if cv2 is None:
        raise HTTPException(status_code=500, detail="opencv-python-headless is required")
    raw = await image.read()
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse({"error": "bad image"}, status_code=400)

    boxes = detect_faces_bgr(img)
    if not STATE["consent_enabled"]:
        img = blur_faces_bboxes(img, boxes)

    model = _get_model()
    label, prob = model.infer_bgr(img)

    resp = {
        "pred": label,
        "score": float(prob),
        "faces": [{"x1":x1,"y1":y1,"x2":x2,"y2":y2} for (x1,y1,x2,y2) in boxes],
        "consent_enabled": STATE["consent_enabled"]
    }
    if return_image:
        resp["image_png_b64"] = _b64_png(img)
    return resp
