## Tasks 1–2: AutoML & Boosting Baselines

1. **AutoML frameworks**  
   Run `python scripts/tabular/automl_baselines.py` to execute AutoGluon, FLAML, and H2O AutoML (if installed). Each framework trains inside a shared StratifiedKFold loop, records accuracy/F1/ROC-AUC per fold in `reports/metrics/automl_baselines.csv`, and appends mean F1 to `reports/metrics/runs.csv`.

2. **Boosting experts**  
   Run `python scripts/tabular/boosting_baselines.py` to tune LightGBM, XGBoost, and CatBoost via Optuna. Each model saves `models/tabular/boosting/<model>/best_params.json`, retrains on the full dataset, keeps feature importance, and logs per-fold metrics to `reports/metrics/boosting_baselines.csv`.

### Notes
- Install the optional dependencies (`autogluon.tabular`, `flaml`, `h2o`, `xgboost`, `catboost`) from `backend/requirements-optional.txt` before running the scripts.  
- The scripts share the dataset/split configuration defined in `configs/tabular/lightgbm_hpo.yml`, so you only need to point that file at your CSV.  
- Use these CSVs to populate your dashboards (e.g., Metrics tab, reports/explain) and compare the modern AutoML baselines versus your custom LightGBM pipeline.
