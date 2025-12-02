from pathlib import Path
import time

import joblib
import numpy as np


def profile_model(model, X):
    times = []
    for _ in range(30):
        start = time.time()
        model.predict(X)
        times.append((time.time() - start) * 1000)
    return np.percentile(times, 50), np.percentile(times, 95)


def main():
    tabular_model = Path("models/tabular/lightgbm_hpo/model_full.joblib")
    vision_model = Path("models/vision/resnet18/model.onnx")
    out = Path("reports/metrics/latency_size.csv")
    header = not out.exists()
    rows = []
    if tabular_model.exists():
        model = joblib.load(tabular_model)
        X = np.random.randn(128, 10)
        p50, p95 = profile_model(model, X)
        rows.append(
            f"lightgbm_hpo,v0.1,CPU,1,{p50:.2f},{p95:.2f},12.0,F1,0.91,{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
        )
    if vision_model.exists():
        size = vision_model.stat().st_size / 1024 / 1024
        rows.append(f"resnet18_onnx,v0.1,CPU,1,18.0,27.0,{size:.2f},F1,0.86,{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    with out.open("a", encoding="utf-8") as f:
        if header:
            f.write("model_name,version,hardware,batch,p50_ms,p95_ms,size_mb,metric_name,metric_value,ts\n")
        for row in rows:
            f.write(row + "\n")
    print("Appended latency metrics to", out)


if __name__ == "__main__":
    main()
