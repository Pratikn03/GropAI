from pathlib import Path
import cv2
import numpy as np
from csv import DictWriter

IMG_ROOT = Path("data/raw/vision/test")
OUT = Path("reports/privacy_utility/blur_sweep.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return CASCADE.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

def face_score(faces, img_gray):
    if len(faces) == 0:
        return 0.0
    scores = []
    for (x, y, w, h) in faces:
        roi = img_gray[y : y + h, x : x + w]
        scores.append(float(cv2.Laplacian(roi, cv2.CV_64F).var()))
    return float(sum(scores) / len(scores))

def sweep():
    images = sorted(IMG_ROOT.rglob("*.jpg")) + sorted(IMG_ROOT.rglob("*.png"))
    kernels = [3, 7, 11, 17, 23, 31]
    rows = []
    for k in kernels:
        utils = []
        privs = []
        for path in images[:200]:
            img = cv2.imread(str(path))
            if img is None:
                continue
            blurred = cv2.GaussianBlur(img, (k, k), 0)
            faces = detect_faces(blurred)
            utilities = len(faces)
            priv_score = face_score(faces, cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY))
            utils.append(utilities)
            privs.append(1.0 / (1.0 + priv_score))
        rows.append(
            {
                "kernel": k,
                "utility": float(np.mean(utils)) if utils else 0.0,
                "privacy": float(np.mean(privs)) if privs else 0.0,
            }
        )
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = DictWriter(f, fieldnames=["kernel", "utility", "privacy"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print("Wrote privacy-utility frontier to", OUT)


if __name__ == "__main__":
    sweep()
