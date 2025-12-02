import json
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
import optuna
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold

RESULTS_DIR = Path("reports/metrics")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    cfg_path = Path("configs/tabular/lightgbm_hpo.yml")
    default = {
        "csv_path": "data/raw/tabular/data.csv",
        "target": "label",
        "n_trials": 25,
        "seed": 42,
    }
    if cfg_path.exists():
        default.update(json.loads(cfg_path.read_text(encoding="utf-8")))
    return default


def report_fold(model_name, dataset, fold, metrics, elapsed):
    file = RESULTS_DIR / "boosting_baselines.csv"
    header = not file.exists()
    row = {
        "model": model_name,
        "dataset": dataset,
        "fold": fold,
        "accuracy": metrics["accuracy"],
        "f1": metrics["f1"],
        "time_s": elapsed,
    }
    with file.open("a", encoding="utf-8") as f:
        if header:
            f.write(",".join(row.keys()) + "\n")
        f.write(",".join(str(row[k]) for k in row) + "\n")


def log_run(model_name, metric):
    file = RESULTS_DIR / "runs.csv"
    header = not file.exists()
    row = {
        "run_id": int(perf_counter()),
        "task": "boosting_baseline",
        "model": model_name,
        "fold": "mean",
        "metric_name": "F1",
        "metric_value": round(metric, 6),
        "split": "cv",
        "ts": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with file.open("a", encoding="utf-8") as f:
        if header:
            f.write(",".join(row.keys()) + "\n")
        f.write(",".join(str(row[k]) for k in row) + "\n")


def run_model(name, classifier_fn, param_sampler, X, y, cfg):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=cfg["seed"])

    def objective(trial):
        params = param_sampler(trial)
        scores = []
        for tr, va in skf.split(X, y):
            clf = classifier_fn(**params)
            clf.fit(X.iloc[tr], y.iloc[tr])
            preds = clf.predict(X.iloc[va])
            scores.append(f1_score(y.iloc[va], preds))
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=cfg["n_trials"])
    best_params = study.best_params
    model_dir = Path("models/tabular/boosting") / name
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "best_params.json").write_text(json.dumps(best_params, indent=2), encoding="utf-8")

    best_clf = classifier_fn(**best_params)
    best_clf.fit(X, y)
    joblib.dump(best_clf, model_dir / "model_full.joblib")

    importances = getattr(best_clf, "feature_importances_", None)
    if importances is not None:
        feat_df = pd.DataFrame(
            {"feature": X.columns, "importance": importances}
        ).sort_values("importance", ascending=False)
        feat_df.to_csv(model_dir / "feature_importance.csv", index=False)

    fold_metrics = []
    for fold, (tr, va) in enumerate(skf.split(X, y)):
        clf = classifier_fn(**best_params)
        start = perf_counter()
        clf.fit(X.iloc[tr], y.iloc[tr])
        preds = clf.predict(X.iloc[va])
        elapsed = perf_counter() - start
        metrics = {
            "accuracy": accuracy_score(y.iloc[va], preds),
            "f1": f1_score(y.iloc[va], preds),
        }
        fold_metrics.append(metrics["f1"])
        report_fold(name, Path(cfg["csv_path"]).stem, fold, metrics, elapsed)

    log_run(name, np.mean(fold_metrics))


def safe_run_model(name, module_name, classifier_fn, param_sampler, X, y, cfg):
    try:
        __import__(module_name)
    except ImportError:
        print(f"Skipping {name}: {module_name} not installed.")
        return
    run_model(name, classifier_fn, param_sampler, X, y, cfg)


def main():
    cfg = load_config()
    df = pd.read_csv(cfg["csv_path"])
    X = df.drop(columns=[cfg["target"]])
    y = df[cfg["target"]]
    if y.nunique() < 2:
        raise SystemExit("Target must be binary for boosting baselines.")

    safe_run_model(
        "LightGBM",
        "lightgbm",
        lambda **p: __import__("lightgbm").LGBMClassifier(
            objective="binary", n_estimators=100, **p
        ),
        lambda trial: {
            "num_leaves": trial.suggest_int("num_leaves", 16, 256),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
        },
        X,
        y,
        cfg,
    )
    safe_run_model(
        "XGBoost",
        "xgboost",
        lambda **p: __import__("xgboost").XGBClassifier(
            use_label_encoder=False, eval_metric="logloss", **p
        ),
        lambda trial: {
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "reg_lambda": trial.suggest_float("reg_lambda", 0.1, 5.0),
        },
        X,
        y,
        cfg,
    )
    safe_run_model(
        "CatBoost",
        "catboost",
        lambda **p: __import__("catboost").CatBoostClassifier(
            verbose=0, **p
        ),
        lambda trial: {
            "depth": trial.suggest_int("depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        },
        X,
        y,
        cfg,
    )


if __name__ == "__main__":
    main()
