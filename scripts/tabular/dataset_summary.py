from pathlib import Path

import pandas as pd


def main():
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    cfg = {"csv_path": "data/raw/tabular/data.csv"}
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    df = pd.read_csv(cfg["csv_path"])
    summary = df.describe(include="all").transpose()
    out = Path("reports/metrics/dataset_summary.csv")
    summary.to_csv(out)
    print("Wrote dataset summary to", out)


if __name__ == "__main__":
    main()
