# Novelty Plan

1. **Governance risk:** expose `/governance/risk_score` that summarizes leakage/data/image issues into a single 0–100 risk number.
2. **Privacy–Utility frontier:** `scripts/vision/blur_sweep.py` sweeps blur kernels to produce `reports/privacy_utility/blur_sweep.csv` for plotting.
3. **ExplainAlign stub:** `scripts/explain/align_score.py` generates pseudo alignment scores aggregating SHAP outputs.
4. **LeakBench-MM skeleton:** `benchmarks/leakbench_mm/run_eval.py` runs HPO under leaky vs safe splits and writes sentinel files.
5. **RAG helper:** `backend/app/routers/rag_helpers.py` powers `/chat/ask` with ANN hits so the UI can cite actual docs.
6. **ExplainAlign:** `scripts/explain/align_metric.py` computes Align@K between SHAP top features and RAG passages to reduce hallucinations.
7. **Risk calibration:** `scripts/governance/risk_calibration.py` correlates governance score with incidents/drift alarms for operational trust.
8. **Policy search:** `scripts/vision/privacy_policy_search.py` selects blur kernels meeting mAP constraints while minimizing identifiability.
