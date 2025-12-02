from pathlib import Path
import json, numpy as np, pandas as pd, shap, joblib, matplotlib.pyplot as plt

CFG = Path("configs/tabular/lightgbm_hpo.yml")
cfg = json.loads(Path(CFG).read_text())
csv_path = Path(cfg.get("csv_path", "data/raw/tabular/data.csv"))
target   = cfg.get("target", "label")
out_dir  = Path("reports/explain/tabular/demo"); out_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)
y = df[target].astype(int); X = df.drop(columns=[target])

model = joblib.load("models/tabular/lightgbm_hpo/model_full.joblib")
explainer = shap.TreeExplainer(model)
shap_vals = explainer.shap_values(X)  # binary: returns list [class0, class1]

sv = shap_vals[1] if isinstance(shap_vals, list) else shap_vals

plt.figure()
shap.summary_plot(sv, X, show=False, plot_type="bar")
plt.tight_layout()
plt.savefig(out_dir/"global_importance_bar.png", dpi=300)
plt.close()

for i in range(min(3, len(X))):
    plt.figure()
    shap.plots._waterfall.waterfall_legacy(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value, sv[i], feature_names=list(X.columns), max_display=12, show=False)
    plt.tight_layout()
    plt.savefig(out_dir/f"sample_{i}_waterfall.png", dpi=300)
    plt.close()

print("Saved SHAP plots to", out_dir)
