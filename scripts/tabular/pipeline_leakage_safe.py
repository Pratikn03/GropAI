from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, PowerTransformer


def build_pipeline(df: pd.DataFrame, target: str, poly: bool = False) -> Pipeline:
    num_cols = df.select_dtypes(include="number").columns.drop(target)
    cat_cols = df.select_dtypes(include="object").columns

    num_transformers = [
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]
    if poly:
        num_transformers.append(("power", PowerTransformer()))
    num_pipe = Pipeline(num_transformers)

    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("oh", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [("num", num_pipe, list(num_cols)), ("cat", cat_pipe, list(cat_cols))], remainder="drop"
    )

    pipeline = Pipeline([("preprocess", preprocessor), ("clf", LogisticRegression(max_iter=400))])
    return pipeline


def main():
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    cfg = {"csv_path": "data/raw/tabular/data.csv", "target": "label"}
    if cfg_path.exists():
        cfg.update(__import__("json").loads(cfg_path.read_text()))
    df = pd.read_csv(cfg["csv_path"])
    target = cfg["target"]
    pipe = build_pipeline(df, target, poly=True)
    pipe.fit(df.drop(columns=[target]), df[target])
    out = Path("models/tabular/leakage_safe")
    out.mkdir(parents=True, exist_ok=True)
    import joblib

    joblib.dump(pipe, out / "pipeline.joblib")
    print("Leakage-safe pipeline saved to", out / "pipeline.joblib")


if __name__ == "__main__":
    main()
