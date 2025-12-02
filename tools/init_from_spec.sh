#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

mkdir -p tools

w() {
  mkdir -p "$(dirname "$1")"
  cat > "$1"
  echo "wrote $1"
}

echo "Initializing project tree from ProjectSpec"

w backend/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.2
numpy==2.1.3
pandas==2.2.3
scikit-learn==1.5.2
onnxruntime==1.19.2
lightgbm==4.5.0
optuna==3.6.1
opencv-python-headless==4.10.0.84
joblib==1.4.2
shap==0.46.0
python-multipart==0.0.9
matplotlib==3.9.2
PyYAML==6.0.2
pyarrow==17.0.0
EOF

w backend/requirements-optional.txt <<'EOF'
torch
torchvision
faiss-cpu
librosa
statsmodels
EOF

for file in backend/app/routers auth privacy chat vision audio rag explain metrics train telemetry nlp features; do
  w backend/app/routers/$file.py <<EOF
from fastapi import APIRouter

router = APIRouter()

@router.get('/ping')
def ping():
    return {'router': '$file'}
EOF
done

w backend/app/routers/__init__.py <<'EOF'
from . import auth, privacy, chat, vision, audio, rag, explain, metrics, train, telemetry, nlp, features
EOF

w backend/app/main.py <<'EOF'
from fastapi import FastAPI
from .routers import auth, privacy, chat, vision, audio, rag, explain, metrics, train, telemetry, nlp, features

app = FastAPI(title="SocialSense-SLM")

routers = [auth, privacy, chat, vision, audio, rag, explain, metrics, train, telemetry, nlp, features]
for router in routers:
    prefix = f"/{router.__name__.split('.')[-1]}"
    app.include_router(router.router, prefix=prefix)

@app.get("/")
def root():
    return {"ok": True, "service": "SocialSense-SLM"}
EOF

w backend/app/services/__init__.py <<'EOF'
""".services package"""
EOF

w backend/app/services/state.py <<'EOF'
from typing import TypedDict

class AppState(TypedDict):
    consent_enabled: bool

STATE: AppState = {"consent_enabled": False}
EOF

w backend/app/services/vision_infer.py <<'EOF'
"""\nVision placeholder\nEOF'
EOF

w backend/app/services/blur.py <<'EOF'
"""\nBlur placeholder\nEOF'
EOF

w backend/app/services/guardrails.py <<'EOF'
"""\nGuardrails stub\nEOF'
EOF

w backend/app/services/metrics_utils.py <<'EOF'
"""\nMetrics utils stub\nEOF'
EOF

w backend/app/services/splits.py <<'EOF'
"""\nSplits helper stub\nEOF'
EOF

for f in tests/test_train_integration tests/test_rag_integration tests/test_explain_integration; do
  w backend/app/tests/$f.py <<'EOF'
def test_placeholder():
    assert True
EOF
done

w backend/app/tests/__init__.py <<'EOF'
""".tests package"""
EOF

w backend/Dockerfile <<'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/app .
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

w frontend/package.json <<'EOF'
{"name":"frontend","version":"0.1.0","scripts":{"dev":"vite","build":"vite build"},"dependencies":{"react":"18.2.0","react-dom":"18.2.0"},"devDependencies":{"vite":"5.0.0","typescript":"5.1.0","@types/react":"18.2.0","@types/react-dom":"18.2.0"}}
EOF

w frontend/tsconfig.json <<'EOF'
{"compilerOptions":{"jsx":"react-jsx","moduleResolution":"node","target":"ESNext","module":"ESNext","esModuleInterop":true,"strict":true},"include":["src"]}
EOF

w frontend/vite.config.ts <<'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({plugins:[react()]})
EOF

w frontend/public/favicon.ico <<'EOF'
icon-placeholder
EOF

w frontend/Dockerfile.prod <<'EOF'
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend .
RUN npm install && npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EOF

w frontend/src/main.tsx <<'EOF'
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles/app.css'
createRoot(document.getElementById('root')!).render(<App/>)
EOF

w frontend/src/App.tsx <<'EOF'
import React from 'react'
const App=()=> <div><h1>SocialSense App</h1></div>
export default App
EOF

w frontend/src/App.tsx <<'EOF'
import React from 'react'
const App=()=> <div><h1>SocialSense App</h1></div>
export default App
EOF

w frontend/src/styles/app.css <<'EOF'
body{font-family:sans-serif;margin:0;padding:0;background:#f4f4f4;}
EOF

w frontend/src/services/api.ts <<'EOF'
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export async function apiGet(path: string){return fetch(API_BASE + path).then(r=>r.json())}
EOF

for comp in Chat VisionStudio AudioStudio Metrics PrivacyConsent Datasets; do
  w frontend/src/components/$comp.tsx <<'EOF'
import React from 'react'
export default function $comp(){return <div>$comp placeholder</div>}
EOF
done

w frontend/src/index.html <<'EOF'
<!doctype html><html><head><meta charset="utf-8"/><title>SocialSense</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>
EOF

w scripts/rag/ingest_docs.py <<'EOF'
print("rag ingest stub")
EOF

w scripts/rag/build_ann.py <<'EOF'
print("rag ann stub")
EOF

for script in scripts/tabular/hpo_lightgbm_optuna.py scripts/tabular/shap_report.py scripts/tabular/shap_batch.py scripts/tabular/calibration.py scripts/tabular/threshold_search.py scripts/tabular/eval_report.py scripts/tabular/dataset_summary.py scripts/tabular/leakage_audit.py scripts/tabular/pipeline_leakage_safe.py; do
  w "$script" <<'EOF'
print("placeholder for $(basename "$script")")
EOF
done

for script in scripts/data/kfold_split.py scripts/data/groupkfold_split.py scripts/data/timeseries_split.py scripts/data/validate_csv.py scripts/data/check_images.py scripts/data/dataset_registry.py; do
  w "$script" <<'EOF'
print("placeholder for $(basename "$script")")
EOF
done

for script in scripts/vision/train_torch.py scripts/vision/export_onnx.py scripts/vision/gradcam.py; do
  w "$script" <<'EOF'
print("vision placeholder")
EOF
done

w scripts/audio/feature_extract.py <<'EOF'
print("audio placeholder")
EOF

w scripts/ops/measure_latency.py <<'EOF'
print("latency stub")
EOF

w scripts/features/build_features.py <<'EOF'
print("features build")
EOF

w scripts/features/load_features.py <<'EOF'
print("features load")
EOF

w scripts/features/cli.py <<'EOF'
print("features cli")
EOF

w scripts/cli.py <<'EOF'
print("CLI placeholder")
EOF

w configs/tabular/lightgbm_hpo.yml <<'EOF'
{
  "csv_path": "data/raw/tabular/data.csv",
  "target": "label",
  "n_trials": 5,
  "seed": 42
}
EOF

mkdir -p configs/datasets
for cfg in tabular_credit_demo text_demo vision_demo; do
  w configs/datasets/${cfg}.yml <<'EOF'
name: ${cfg}
type: tabular
task: classification
csv_path: data/raw/tabular/data.csv
EOF
done

w configs/vision/resnet18_classification.yml <<'EOF'
epochs: 5
EOF

mkdir -p data/raw/tabular data/raw/text data/raw/vision/train data/raw/vision/val data/raw/vision/test
w data/raw/tabular/data.csv <<'EOF'
f1,f2,label
0.1,1,0
EOF

w data/raw/text/textclf.csv <<'EOF'
text,label
hello,0
EOF

mkdir -p data/metadata/splits
echo "[]" > data/metadata/splits/kfold.json
echo "[]" > data/metadata/splits/groupkfold.json
echo "[]" > data/metadata/splits/timeseries.json

mkdir -p models/rag models/nlp models/tabular/lightgbm_hpo models/vision/resnet18
touch models/rag/tfidf_vectorizer.joblib
echo "{}" > models/rag/docs.jsonl
echo "{}" > models/nlp/textclf.joblib
echo "{}" > models/tabular/lightgbm_hpo/best_params.json
echo "{}" > models/tabular/lightgbm_hpo/model_full.joblib
echo "{}" > models/tabular/lightgbm_hpo/model_calibrated.joblib
echo "0.5" > models/tabular/lightgbm_hpo/best_threshold.txt
touch models/vision/resnet18/model.onnx
echo "label1" > models/vision/resnet18/labels.txt
touch models/vision/resnet18/resnet18.pt

mkdir -p reports/metrics reports/explain/tabular/demo reports/explain/tabular/batch reports/explain/vision reports/figures/tabular
touch reports/metrics/runs.csv reports/metrics/latency_size.csv reports/metrics/leakage_audit.json reports/metrics/data_validation.json reports/metrics/image_validation.txt reports/metrics/classification_report.txt
touch reports/explain/tabular/demo/global_importance_bar.png
touch reports/explain/tabular/demo/sample_0_waterfall.png
touch reports/explain/tabular/demo/sample_1_waterfall.png
touch reports/explain/tabular/demo/sample_2_waterfall.png
touch reports/explain/tabular/batch/global_importance.csv
touch reports/explain/tabular/batch/per_sample_topk.csv
touch reports/figures/tabular/roc_curve.png
touch reports/figures/tabular/pr_curve.png

mkdir -p feature_store/features/v1/date=20240101
w feature_store/manifest.json <<'EOF'
{"active_version":"v1","versions":{"v1":[{"date":"20240101","path":"feature_store/features/v1/date=20240101/features.parquet"}]}}
EOF
touch feature_store/features/v1/date=20240101/features.parquet

w docker-compose.prod.yml <<'EOF'
version: "3.9"
services: {}
EOF

mkdir -p docker/prod deploy/monitoring
w docker/prod/nginx.conf <<'EOF'
events {}
http { server { listen 80; location / { return 200; } } }
EOF

w deploy/monitoring/prometheus.yml <<'EOF'
global: {}
EOF

w .github/workflows/ci-smoke.yml <<'EOF'
name: smoke
on: push
jobs: {}
EOF

mkdir -p docs
for doc in README.md docs/OVERVIEW.md docs/API.md docs/DATA_GOVERNANCE.md docs/PRIVACY.md docs/EVALUATION.md docs/MLOPS.md docs/ROADMAP.md; do
  w "$doc" <<'EOF'
# ${doc##*/}
placeholder content
EOF
done

echo "Project scaffolded from ProjectSpec v2.4."
