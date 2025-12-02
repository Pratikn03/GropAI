from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score


def main():
    cfg = {"csv_path": "data/raw/tabular/data.csv", "target": "label"}
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    model_path = Path("models/tabular/lightgbm_hpo/model_full.joblib")
    if not model_path.exists():
        raise SystemExit("Model missing.")
    df = pd.read_csv(cfg["csv_path"])
    X = df.drop(columns=[cfg["target"]])
    model = joblib.load(model_path)
    prob = model.predict_proba(X)[:, 1]
    thresholds = np.linspace(0.1, 0.9, 81)
    best = {"threshold": 0.5, "f1": 0.0}
    for thr in thresholds:
        preds = (prob >= thr).astype(int)
        score = f1_score(df[cfg["target"]], preds)
        if score > best["f1"]:
            best = {"threshold": thr, "f1": score}
    out = Path("models/tabular/lightgbm_hpo/best_threshold.txt")
    out.write_text(f"{best['threshold']}\nF1={best['f1']:.4f}", encoding="utf-8")
    print("Best threshold written to", out)


if __name__ == "__main__":
    main()
