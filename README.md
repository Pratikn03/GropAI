# SocialSense-SLM (Flagship v2)

SocialSense-SLM is a multi-modal experimentation stack that pairs a FastAPI backend, a Vite/React frontend, and a catalog of tooling for running locally hosted RAG, vision, metrics, and training workloads. It routes telemetry and privacy signals through controllers so each layer can be exercised independently while retaining simple scripts for building and shipping artifacts.

## Highlights

- **Backend** (`backend/`): FastAPI app with routers for chat-based retrieval, vision inference (ONNX ResNet18), privacy toggles, telemetry/metrics, and training flows. The service keeps a consent state that blurs detected faces before classification whenever users opt-out.
- **Frontend** (`frontend/`): Vite + React + TypeScript starter with a component library ready for social-sensing dashboards and was built to pair with the backend APIs.
- **Model vaults** (`models/`): RAG artifacts (`tfidf_vectorizer.joblib`, `tfidf_matrix.joblib`, `docs.jsonl`) plus vision assets are expected under `models/rag/` and `models/vision/`.
- **Support tooling** (`scripts/`): RAG index builders (`scripts/rag`), vision training helpers (`scripts/vision`), tabular HPO/shap reporting (`scripts/tabular`), and operation helpers for docker builds or multi-service runs (`scripts/ops`).
- **Governance** (`docs/`, `.github/`): Lifecycle writeups, data/model card templates, and GitHub workflows for CI/data checks provide an observability layer for the flagship project.

## Repository Layout

- `.github/`: CI/data-check workflow definitions.
- `backend/`: API routes, services, Dockerfile, requirements, and env template.
- `frontend/`: Vite app, npm metadata, shared styles, and component stubs.
- `configs/`: Sample configurations for application and experiment launches.
- `docs/`: Lifecycle narratives, data and model card templates, and architecture imagery.
- `scripts/`: Helpers for building Docker artifacts, ingesting/querying RAG indices, tabular reports, and vision utilities.
- `models/`: Placeholder for pre-trained resnet and RAG resources (not checked into Git by default).
- `reports/`: Metrics summaries (currently `.gitkeep` to preserve the directory).
- `docker-compose.yml`: skeleton for orchestrating services when a compose manifest grows.

## Getting Started

### Backend API

1. Create a Python 3.11+ virtual environment: `python -m venv .venv && source .venv/bin/activate`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Copy the env template and rotate secrets: `cp backend/.env.example backend/.env` and edit `SECRET_KEY`.
4. Start the server: `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload`.

Available routers: `/chat/ask`, `/vision/infer`, `/privacy/consent`, `/metrics/*`, `/telemetry/*`, `/train/*`, `/audio/*`, `/auth/*`, and `/rag/*`. The `/chat/ask` endpoint uses a TF-IDF retrieval stack over `models/rag`.

### Frontend UI

1. `cd frontend`
2. Install packages: `npm install`
3. Run the dev server: `npm run dev -- --host`

The React tree is scaffolded to consume the backend APIs via `frontend/src/services/api.ts`.

### Models & Data

- Pre-built RAG artifacts must be placed under `models/rag/` (`tfidf_vectorizer.joblib`, `tfidf_matrix.joblib`, `docs.jsonl`). Use `scripts/rag/ingest_docs.py` and `build_index.py` to refresh them.
- Vision models live under `models/vision/resnet18/`. Rebuild or replace these assets through the training helpers in `scripts/vision`.
- Tabular experiments live under `configs/tabular/` and can be exercised through `scripts/tabular`.

### Containers & Ops

- `backend/Dockerfile` and `frontend/Dockerfile` can be extended to build production images.
- Operational helpers: `scripts/ops/build_docker.sh` (wraps docker build) and `scripts/ops/run_all.sh`.
- `docker-compose.yml` stays empty for now but is the placeholder for wiring backend, frontend, and optional data services together.

## Documentation & Governance

- Lifecycle posts: `docs/lifecycle/00_overview.md` through `appendix_40.md` offer guided insights for running SocialSense.
- Design artifacts: `docs/figures/SocialSense_one_slide_architecture.{png,svg}`.
- Governance templates: `docs/data_cards/template.md`, `docs/model_cards/template.md` for recording dataset/model metadata.
- CI: GitHub workflows in `.github/workflows` validate the stack against required checks.

## Testing & Metrics

- Backend test stubs: `backend/tests/test_001.py` through `test_160.py` show intent to cover edge cases (run via pytest when fleshing out).
- Metrics telemetry hooks exist under `backend/app/routers/metrics.py` and `telemetry.py`.
- Use `scripts/tabular/shap_report.py` to generate explainability reports after training with `scripts/tabular/hpo_lightgbm_optuna.py`.

## Troubleshooting

- Ensure required models/data live under `models/` before hitting `/chat/ask` or `/vision/infer`.
- Face blurring is governed by `privacy/consent`; hit `/privacy/consent` POST to enable/disable blur protection.
- Use `uvicorn` logs plus FastAPI docs (`/docs`) to inspect running routes.

## Contributing

- Follow the lifecycle documented in `docs/lifecycle`.
- Update the templates under `docs/data_cards` / `docs/model_cards` when onboarding new datasets or models.
- Keep `.github/workflows` aligned with the checks you need (CI/data-checks shown as examples).

## License

No license file is included; add one (e.g., `MIT`, `Apache-2.0`) if you intend to share this repository publicly.
