from pathlib import Path

import joblib
import pandas as pd
import shap


def main():
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    cfg = {"csv_path": "data/raw/tabular/data.csv", "target": "label"}
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    df = pd.read_csv(cfg["csv_path"])
    model_path = Path("models/tabular/lightgbm_hpo/model_full.joblib")
    if not model_path.exists():
        raise SystemExit("Model artifact missing.")
    model = joblib.load(model_path)
    X = df.drop(columns=[cfg["target"]])
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    out_dir = Path("reports/explain/tabular/batch")
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(shap_values).to_csv(out_dir / "per_sample_shap.csv", index=False)
    pd.Series(X.columns).to_csv(out_dir / "global_importance.csv", index=False)
    print("Saved SHAP batch outputs to", out_dir)


if __name__ == "__main__":
    main()
