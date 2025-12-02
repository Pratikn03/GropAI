✅ SocialSense-SLM — Master Checklist (for Code Assistant)

Goal: Privacy-aware, leakage-audited multimodal system (vision + audio + tabular + small LLM/RAG) with explainable, deployable endpoints.
Repo baseline: You already downloaded SocialSense-SLM-flagship-fullstack.zip and unzipped to repo root.

⸻

0) One-screen project brief (tell the AI assistant)
	•	Frontend: React/Vite app (chat + webcam/mic tiles; tabs: Chat, Vision Studio, Audio Studio, Metrics, Privacy, Admin).
	•	Backend: FastAPI with routers: /auth, /privacy, /chat, /vision, /audio, /rag, /metrics, /train, /telemetry.
	•	Models:
	•	Vision: PyTorch ResNet-18 → ONNX Runtime (real-time).
	•	Tabular: LightGBM + Optuna HPO (folded CV) + SHAP.
	•	NLP: small LLM with local RAG (sqlite-vss/FAISS).
	•	Storage: DVC → Google Drive (Shared Drive) as source of truth; train from local NVMe; optional GCS/S3 mirror.
	•	Guardrails: consent ledger + auto face-blur when consent OFF; leakage-safe splits (KFold/GroupKFold/TimeSeriesSplit); p-values & CIs.
	•	Deliverables: metrics tables, SHAP & Grad-CAM, Pareto (accuracy/latency/size), Dockerized demo.

⸻

1) Immediate setup (once)
	•	Create Google Shared Drive (e.g., SLMS_DATA) → copy folder ID.
	•	In repo root:

make dvc-init DRIVE_ID=<YOUR_SHARED_DRIVE_FOLDER_ID>

	•	(Optional CI) Put service account JSON at .secrets/gdrive-sa.json then:

dvc remote modify gdrive gdrive_use_service_account true
dvc remote modify gdrive gdrive_service_account_json_path .secrets/gdrive-sa.json

	•	Install deps:

make install-backend
make install-frontend


⸻

2) Data layout & sharding (training-ready)

Where files live
	•	data/raw/ — temporary raw drops (won’t be tracked in Git).
	•	data/shards/ — final WebDataset/JSONL.gz/Parquet shards (DVC-tracked).
	•	data/metadata/splits/ — JSON split indices.
	•	data/metadata/manifests/ — SHA256 lists of shards.
	•	data/metadata/licenses/ — dataset licenses/consent docs.

Shard formats
	•	Vision: data/shards/cv/cv-train-000000.tar (~1 GB each; ~10k JPEGs/shard)
	•	Audio: data/shards/audio/audio-train-000000.tar (256 MB–1 GB)
	•	Text: data/shards/text/text-000000.jsonl.gz (512 MB–1 GB)
	•	Tabular: Parquet or CSV inside TAR shards

Make shards (replace demo sources later):

python scripts/data/make_image_shards.py
python scripts/data/make_audio_shards.py
python scripts/data/make_text_shards.py
python scripts/data/compute_sha256_manifest.py

Track & push shards:

dvc add data/shards data/metadata/splits
git add data/shards.dvc data/metadata/splits.dvc .dvc .gitignore .dvcignore
git commit -m "Track shards & splits"
dvc push -r gdrive --jobs 8


⸻

3) Leakage guard & splits (must be clean before training)
	•	Choose split type per dataset:
	•	StratifiedKFold — standard classification.
	•	GroupKFold — multiple samples per person/session (prevents identity leakage).
	•	TimeSeriesSplit — temporal ordering (prevents look-ahead).
	•	Generate example split JSONs (replace with real indices later):

python scripts/data/kfold_split.py
python scripts/data/groupkfold_split.py
python scripts/data/timeseries_split.py


	•	Guard checks (duplicates, group leakage, label tokens in filenames) — implement in scripts/data/verify_storage.py; CI runs .github/workflows/data-checks.yml.

Definition of Done: Every dataset has: (a) a split JSON, (b) leakage guard report, (c) a data card in docs/data_cards/.

⸻

4) Training (tabular) — LightGBM + Optuna + SHAP
	•	Prepare CSV/Parquet with a label column (edit configs/tabular/lightgbm_hpo.yml).
	•	Run HPO (uses 5-fold CV by default):

python scripts/tabular/hpo_lightgbm_optuna.py configs/tabular/lightgbm_hpo.yml

	•	Save artifacts:
	•	models/tabular/lightgbm_hpo/best_params.json
	•	reports/metrics/runs.csv (append results)
	•	(Then) implement SHAP:

python scripts/tabular/shap_report.py

Store plots in reports/explain/tabular/<dataset>/.

Acceptance: Mean ± SD across folds, 95% CI, paired test vs AutoML baseline.

⸻

5) Training (vision) — PyTorch → ONNX → ORT
	•	Place class folders under data/raw/cv/train and data/raw/cv/valid.
	•	Train:

python scripts/vision/train_pytorch.py --config configs/vision/resnet18_classification.yml

	•	Export ONNX:

python scripts/vision/export_vision_onnx.py configs/vision/resnet18_classification.yml

	•	Generate Grad-CAM exemplars (implement in scripts/vision/grad_cam.py) → save under reports/explain/vision/.
	•	DVC-track models/ and push.

Targets: CPU p95 < 60 ms/frame, GPU p95 < 20 ms; model size small (< ~50 MB fp16 ONNX if possible).

⸻

6) AutoML baselines (fair comparison)
	•	Integrate AutoGluon / LightAutoML / H2O / FLAML with identical folds and time budgets (300–600s).
	•	Save per-fold metrics and runtimes to reports/metrics/.
	•	Build summary tables (mean ± SD, 95% CI, p-value vs LGBM HPO).

⸻

7) RAG & small LLM
	•	Ingest docs: scripts/rag/ingest_docs.py (chunk → embed → index).
	•	Build index: scripts/rag/build_index.py (sqlite-vss default; FAISS if available).
	•	Add refusal policy: if retrieval score < τ, answer “I don’t have enough evidence” and ask a clarifying question.
	•	Log retrieval hits/misses to reports/metrics/rag.csv.

Acceptance: Answers show citations; out-of-scope queries produce refusals, not hallucinations.

⸻

8) Privacy, consent & safety
	•	Implement consent ledger in /privacy:
	•	States: enabled: true/false, video_store: allow/block, audio_store: allow/block, embed_store: allow/block.
	•	Auto face-blur path in vision pipeline when consent OFF.
	•	PII redaction for transcripts before indexing (simple regex + allowlist).
	•	Add rate limits / input caps on API to prevent abuse.

⸻

9) Frontend wiring
	•	Set VITE_API_URL → backend base URL.
	•	Chat tab → calls /chat/ask and displays citations; “Why?” → pulls SHAP or Grad-CAM image.
