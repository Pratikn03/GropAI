#/bin/bash
set -euo pipefail

echo "1. ensure splits"
python scripts/data/kfold_split.py || true
python scripts/data/groupkfold_split.py || true
python scripts/data/timeseries_split.py || true

echo "2. guardrails + leakage audit"
python scripts/tabular/leakage_audit.py

echo "3. dataset summary"
python scripts/tabular/dataset_summary.py

echo "4. run LightGBM HPO"
python scripts/tabular/hpo_lightgbm_optuna.py configs/tabular/lightgbm_hpo.yml

echo "5. boosting baselines"
python scripts/tabular/boosting_baselines.py

echo "6. AutoML baselines"
python scripts/tabular/automl_baselines.py

echo "7. SHAP/Explain files"
python scripts/tabular/shap_report.py
python scripts/tabular/shap_batch.py

echo "8. explain alignment metrics"
python scripts/explain/align_metric.py || true

echo "8. stats and eval"
python scripts/tabular/eval_report.py
python scripts/tabular/calibration.py
python scripts/tabular/threshold_search.py

echo "9. latency & ops metrics"
python scripts/ops/measure_latency.py
echo "10. governance calibration + policy"
python scripts/governance/risk_calibration.py || true
python scripts/governance/compute_risk_correlation.py || true
python scripts/vision/privacy_policy_search.py || true
python scripts/vision/pu_auc.py || true
echo "Run complete."
