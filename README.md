# SocialSense-SLM — Flagship v2.6+

SocialSense-SLM is a **leakage-audited, privacy-first, multimodal AutoML & RAG product** featuring:
- Tabular AutoML (LightGBM/Optuna + SHAP) with modern baselines (AutoGluon/FLAML/H2O), leakage guardrails, and explainability alignment.
- Vision training → ONNX → inference path with consent-aware face blur, privacy–utility sweeps, and policy optimization.
- SBERT-powered RAG (TF-IDF fallback + optional FAISS/Qdrant) plus clear governance risk scoring (0–100) surfaced in the API/UI.
- Feature-store-first reproducibility (versioned snapshots, dataset registry, run-all script) plus operational monitoring (PSI/KS, PU-AUC).

## Highlights

| Pillar | What’s new | Evidence |
| --- | --- | --- |
| **Leakage guardrails** | Tabular pipelines run inside leakage-safe Pipelines + stratified CV; guardrails check duplicates/time/path before training. | `backend/app/services/guardrails.py`, `reports/metrics/leakage_audit.json`, `benchmarks/leakbench_mm/run_eval.py`. |
| **Governance risk** | `/governance/risk_score` aggregates leakage/data/image signals and shows a single score in the UI. | `scripts/governance/risk_calibration.py`, `reports/metrics/governance_calibration.csv`, `frontend/src/components/GovernanceScore.tsx`. |
| **Privacy–utility frontier** | `scripts/vision/blur_sweep.py` sweeps blur kernels, policy search selects the best kernel, and PU-AUC quantifies trade-offs. | `reports/privacy_utility/{blur_sweep.csv,policy_search.csv,pu_auc.csv}`. |
| **ExplainAlign** | Align@K correlates SHAP top features with RAG passages to reduce hallucination. | `reports/explain/align/align_at_k.csv`, `scripts/explain/align_metric.py`. |
| **SBERT RAG** | SBERT embeddings with optional FAISS vector search power `/rag/sbert/search` and chat uses extractive citations. | `scripts/rag/build_sbert.py`, `backend/app/routers/rag_sbert.py`, `backend/app/routers/chat.py`. |
| **Feature store + reproducibility** | Versioned manifest, dataset registry configs, and `scripts/run_all.sh` reproduce everything from splits to reports. | `feature_store/manifest.json`, `configs/datasets/*.yml`, `scripts/run_all.sh`. |

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
# optional heavy deps (SBERT, AutoGluon, FLAML, torch)
pip install -r backend/requirements-optional.txt
```

### Data layout

```
data/
  raw/tabular/data.csv
  raw/vision/{train,val,test}
  raw/text/textclf.csv
```

### Run the full benchmark

```bash
bash scripts/run_all.sh
```

This drives guardrails, LightGBM HPO, boosting/AutoML baselines, SHAP, Align@K, latency metrics, governance calibration, and privacy policy search. Result files land under `reports/metrics/`, `reports/explain/align/`, and `reports/privacy_utility/`.

## Vision workflow

```bash
python scripts/vision/train_torch.py --epochs 2
python scripts/vision/export_onnx.py
python scripts/vision/infer_onnx.py
```

Outputs: `models/vision/resnet18/{model.pt,model.onnx}`.

## API quick commands

```
GET  /health/live              # health
GET  /features/info            # feature store meta
GET  /governance/risk_score    # risk index 0-100
POST /train/tabular/hpo        # run LightGBM+Optuna
POST /train/vision/train       # run Torch trainer
POST /train/rag/build          # SBERT builder
POST /explain/tabular          # SHAP batch
POST /chat/ask                 # TF-IDF/SBERT extractive answer
POST /rag/sbert/search         # SBERT nearest neighbors
POST /privacy/consent          # toggle blur consent
```

## Governance & privacy

- **Risk calibration**: log governance entries to `reports/metrics/governance_history.json` and run `scripts/governance/risk_calibration.py` + `compute_risk_correlation.py`.  
- **ExplainAlign**: `scripts/explain/align_metric.py` creates Align@K scores linking SHAP features to RAG docs.  
- **Privacy policy**: `scripts/vision/blur_sweep.py` + `privacy_policy_search.py` select kernels meeting a utility target; measure PU-AUC via `scripts/vision/pu_auc.py`.

## Monitoring & drift

- `scripts/monitoring/psi_ks.py` compares old vs new tabular distributions (PSI/KS).  
- `scripts/governance/risk_calibration.py` ensures the governance risk score correlates with incidents/drift alarm counts.  
- `scripts/tabular/leakage_audit.py` catches duplicate/path leakage before training.

## Frontend

- Vite/React dashboard with `FeaturesInfo` + `GovernanceScore` widgets, chat, vision, audio, metrics, datasets, and privacy views.  
- `frontend/src/services/api.ts` hits the backend endpoints with optional API key.  
- Use `npm run dev` (after `npm install`) for local UI.

## Testing & CI

```bash
pytest backend/app/tests/test_train_and_explain.py
```

- Extend `.github/workflows` to run `scripts/run_all.sh`, governance scripts, and `psi_ks` as needed.

## TODOs

- 🟢 Provide real datasets/models under `data/raw/` + `models/` before demos.  
- 🟡 Add Pareto plots (accuracy vs latency/size, privacy–utility, Align@K).  
- 🟡 Complete CI workflow that invokes `scripts/run_all.sh`, RAG rebuild, governance calibration, and monitoring.  
- 🔴 Expand docs with figure/table exports (ROC/PR, PU curves, governance risk charts).  
- 🔴 Add dataset-registry UI tests and RAG performance analyses.

```
