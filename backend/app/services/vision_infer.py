from pathlib import Path
from typing import List, Tuple
import onnxruntime as ort
import numpy as np
import cv2
import json

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

def _preprocess_bgr(img_bgr: np.ndarray, size=(224,224)) -> np.ndarray:
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, size, interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    img = (img - IMAGENET_MEAN) / IMAGENET_STD
    x = np.transpose(img, (2,0,1))[None, ...]  # NCHW
    return x.astype(np.float32)

def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=1, keepdims=True)

class VisionONNXService:
    def __init__(self, model_path: str, labels_path: str|None=None):
        providers = ['CPUExecutionProvider']
        self.sess = ort.InferenceSession(model_path, providers=providers)
        self.input_name = self.sess.get_inputs()[0].name
        self.labels = None
        if labels_path and Path(labels_path).exists():
            try:
                if labels_path.endswith(".json"):
                    self.labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
                else:
                    self.labels = [l.strip() for l in Path(labels_path).read_text(encoding="utf-8").splitlines() if l.strip()]
            except Exception:
                self.labels = None

    def infer_bgr(self, img_bgr: np.ndarray) -> tuple[str, float]:
        x = _preprocess_bgr(img_bgr)
        logits = self.sess.run(None, {self.input_name: x})[0]  # (N,C)
        probs = _softmax(logits)
        c = int(np.argmax(probs[0]))
        p = float(probs[0, c])
        label = self.labels[c] if (self.labels and 0 <= c < len(self.labels)) else f"class_{c}"
        return label, p
