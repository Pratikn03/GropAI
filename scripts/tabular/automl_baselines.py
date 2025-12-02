import json
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

RESULTS_DIR = Path("reports/metrics")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    default = {
        "csv_path": "data/raw/tabular/data.csv",
        "target": "label",
        "n_splits": 5,
        "seed": 42,
        "time_budget": 180,
    }
    if cfg_path.exists():
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        default.update(data)
    return default


def compute_metrics(y_true, y_pred, y_prob=None):
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
    }
    if y_prob is not None and len(np.unique(y_true)) == 2:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob[:, 1])
        except Exception:
            metrics["roc_auc"] = None
    else:
        metrics["roc_auc"] = None
    return metrics


def append_results(framework, dataset, fold, metrics, elapsed):
    file = RESULTS_DIR / "automl_baselines.csv"
    header = not file.exists()
    row = {
        "framework": framework,
        "dataset": dataset,
        "fold": fold,
        "accuracy": metrics["accuracy"],
        "f1": metrics["f1"],
        "roc_auc": metrics["roc_auc"],
        "time_s": elapsed,
    }
    with file.open("a", encoding="utf-8") as f:
        if header:
            f.write(",".join(row.keys()) + "\n")
        f.write(",".join(str(row[k]) if row[k] is not None else "" for k in row) + "\n")


def log_summary(framework, dataset, stats):
    file = RESULTS_DIR / "runs.csv"
    header = not file.exists()
    row = {
        "run_id": int(perf_counter()),
        "task": "automl_baseline",
        "model": framework,
        "fold": "mean",
        "metric_name": "F1",
        "metric_value": round(stats["f1_mean"], 6),
        "split": "cv",
        "ts": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with file.open("a", encoding="utf-8") as f:
        if header:
            f.write(",".join(row.keys()) + "\n")
        f.write(",".join(str(row[k]) for k in row) + "\n")


class AutoMLRunner:
    def __init__(self, name, fitter):
        self.name = name
        self.fitter = fitter
        self.available = True

    def run(self, train_df, target, val_df, time_limit):
        predictor = self.fitter(train_df, target, time_limit)
        X_val = val_df.drop(columns=[target])
        y_val = val_df[target]
        preds = predictor.predict(X_val)
        probs = None
        if hasattr(predictor, "predict_proba"):
            probs = predictor.predict_proba(X_val)
        return y_val.values, preds, probs


def make_autogluon_runner():
    try:
        from autogluon.tabular import TabularPredictor
    except ImportError:
        return None

    def fit(train_df, target, time_limit):
        predictor = TabularPredictor(label=target, verbosity=0).fit(
            train_data=train_df, time_limit=time_limit
        )
        return predictor

    return AutoMLRunner("AutoGluon", fit)


def make_flaml_runner():
    try:
        from flaml import AutoML
    except ImportError:
        return None

    def fit(train_df, target, time_limit):
        automl = AutoML()
        automl.fit(
            X_train=train_df.drop(columns=[target]),
            y_train=train_df[target],
            task="classification",
            time_budget=time_limit,
        )
        class Predictor:
            def predict(self, X):
                return automl.predict(X)

            def predict_proba(self, X):
                return automl.predict_proba(X)

        return Predictor()

    return AutoMLRunner("FLAML", fit)


def make_h2o_runner():
    try:
        import h2o
        from h2o.automl import H2OAutoML
    except ImportError:
        return None

    h2o.init(min_mem_size="2G", max_mem_size="4G", ignore_config=True)

    def fit(train_df, target, time_limit):
        train = h2o.H2OFrame(train_df)
        train[target] = train[target].asfactor()
        automl = H2OAutoML(max_runtime_secs=time_limit, seed=42, verbosity="info")
        automl.train(y=target, training_frame=train)

        class Predictor:
            def predict(self, X):
                frame = h2o.H2OFrame(X)
                return automl.leader.predict(frame).as_data_frame()["predict"].values

            def predict_proba(self, X):
                frame = h2o.H2OFrame(X)
                preds = automl.leader.predict(frame).as_data_frame()
                return preds[[c for c in preds.columns if c.startswith("p")]].values

        return Predictor()

    return AutoMLRunner("H2OAutoML", fit)


def main():
    cfg = load_config()
    df = pd.read_csv(cfg["csv_path"])
    target = cfg["target"]
    if target not in df.columns:
        raise SystemExit(f"Target column {target} not found.")
    dataset = Path(cfg["csv_path"]).stem
    skf = StratifiedKFold(n_splits=cfg["n_splits"], shuffle=True, random_state=cfg["seed"])
    runners = [
        make_autogluon_runner(),
        make_flaml_runner(),
        make_h2o_runner(),
    ]
    for nested in runners:
        if nested is None:
            continue
        framework = nested
        fold_metrics = {"f1": [], "accuracy": [], "roc_auc": []}
        for fold, (tr, va) in enumerate(skf.split(df, df[target])):
            train_df = df.iloc[tr].reset_index(drop=True)
            val_df = df.iloc[va].reset_index(drop=True)
            start = perf_counter()
            try:
                y_val, preds, probs = framework.run(train_df, target, val_df, cfg["time_budget"])
            except Exception as exc:
                print(f"[{framework.name}] fold {fold} failed: {exc}", file=sys.stderr)
                break
            elapsed = perf_counter() - start
            metrics = compute_metrics(y_val, preds, probs)
            fold_metrics["f1"].append(metrics["f1"])
            fold_metrics["accuracy"].append(metrics["accuracy"])
            fold_metrics["roc_auc"].append(metrics["roc_auc"])
            append_results(framework.name, dataset, fold, metrics, elapsed)
        if not fold_metrics["f1"]:
            continue
        summary = {
            "f1_mean": mean(fold_metrics["f1"]),
            "f1_std": stdev(fold_metrics["f1"]) if len(fold_metrics["f1"]) > 1 else 0.0,
        }
        log_summary(framework.name, dataset, summary)


if __name__ == "__main__":
    main()
