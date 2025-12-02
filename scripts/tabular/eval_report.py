from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    plot_precision_recall_curve,
    plot_roc_curve,
)


def main():
    cfg = {"csv_path": "data/raw/tabular/data.csv", "target": "label"}
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    df = pd.read_csv(cfg["csv_path"])
    X = df.drop(columns=[cfg["target"]])
    y = df[cfg["target"]]
    model_path = Path("models/tabular/lightgbm_hpo/model_full.joblib")
    if not model_path.exists():
        raise SystemExit("Model missing.")
    model = joblib.load(model_path)
    preds = model.predict(X)
    probs = model.predict_proba(X)
    report = classification_report(y, preds, output_dict=True)
    pd.DataFrame(report).transpose().to_csv("reports/metrics/classification_report.csv")
    out_fig = Path("reports/figures/tabular")
    out_fig.mkdir(parents=True, exist_ok=True)
    plot_roc_curve(model, X, y)
    plt.savefig(out_fig / "roc_curve.png")
    plt.clf()
    plot_precision_recall_curve(model, X, y)
    plt.savefig(out_fig / "pr_curve.png")
    plt.clf()
    print("Saved classification report + ROC/PR curves.")


if __name__ == "__main__":
    main()
