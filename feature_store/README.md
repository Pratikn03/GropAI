# Feature Store (v1)

This directory captures a minimal feature store skeleton:

* **`manifest.json`** tracks snapshot paths, timestamps, and source datasets.
* **`features/v1/date=<YYYYMMDD>/features.parquet`** holds Parquet files written by `scripts/features/build_features.py`.

The pipeline is intentionally simple:

1. Call `scripts/features/cli.py build` to materialize the latest dataset snapshot.
2. Call `scripts/features/cli.py load` to read the newest version for downstream training or inference.
3. Extend the manifest with metadata for reproducibility and potential time-travel queries.

The feature store assumes tabular input data described in `configs/datasets`. The scripts append the latest snapshot information to the manifest automatically.
