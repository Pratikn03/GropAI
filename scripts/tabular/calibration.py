from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV


def main():
    cfg = {"csv_path": "data/raw/tabular/data.csv", "target": "label"}
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    model_path = Path("models/tabular/lightgbm_hpo/model_full.joblib")
    if not model_path.exists():
        raise SystemExit("Base model is missing.")
    df = pd.read_csv(cfg["csv_path"])
    X = df.drop(columns=[cfg["target"]])
    y = df[cfg["target"]]
    model = joblib.load(model_path)
    calib = CalibratedClassifierCV(model, method="isotonic", cv=3)
    calib.fit(X, y)
    out = Path("models/tabular/lightgbm_hpo/model_calibrated.joblib")
    joblib.dump(calib, out)
    with out.parent.joinpath("calibration_info.txt").open("w") as f:
        f.write(f"Calibrated with isotonic on {len(X)} samples.\n")
    print("Saved calibrated model to", out)


if __name__ == "__main__":
    main()
