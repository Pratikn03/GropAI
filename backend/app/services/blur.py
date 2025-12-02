from typing import List, Tuple
import cv2
import numpy as np

def detect_faces_bgr(img_bgr: np.ndarray) -> List[Tuple[int,int,int,int]]:
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(32,32))
    boxes = []
    for (x,y,w,h) in faces:
        boxes.append((int(x), int(y), int(x+w), int(y+h)))
    return boxes

def blur_faces_bboxes(img_bgr: np.ndarray, bboxes: List[Tuple[int,int,int,int]]) -> np.ndarray:
    out = img_bgr.copy()
    for (x1,y1,x2,y2) in bboxes:
        roi = out[y1:y2, x1:x2]
        if roi.size == 0: 
            continue
        roi = cv2.GaussianBlur(roi, (31,31), 25)
        out[y1:y2, x1:x2] = roi
    return out
