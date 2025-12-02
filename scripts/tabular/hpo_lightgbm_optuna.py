import json, argparse, time
from pathlib import Path
import numpy as np, pandas as pd, optuna, lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from joblib import dump

p = argparse.ArgumentParser()
p.add_argument("config")
args = p.parse_args()

cfg = json.loads(Path(args.config).read_text())
csv_path = Path(cfg.get("csv_path", "data/raw/tabular/data.csv"))
target   = cfg.get("target", "label")
n_trials = int(cfg.get("n_trials", 25))
seed     = int(cfg.get("seed", 42))

df = pd.read_csv(csv_path)
y = df[target].astype(int)
X = df.drop(columns=[target])

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

def obj(trial):
    params = {
        "objective": "binary",
        "metric": "None",
        "learning_rate": trial.suggest_float("lr", 1e-3, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 16, 256),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 10, 200),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.5, 1.0),
        "lambda_l1": trial.suggest_float("lambda_l1", 0.0, 5.0),
        "lambda_l2": trial.suggest_float("lambda_l2", 0.0, 5.0),
        "verbose": -1,
        "seed": seed,
    }
    scores=[]
    for tr, va in skf.split(X, y):
        dtr = lgb.Dataset(X.iloc[tr], label=y.iloc[tr])
        dva = lgb.Dataset(X.iloc[va], label=y.iloc[va])
        model = lgb.train(params, dtr, num_boost_round=500, valid_sets=[dva],
                          callbacks=[lgb.early_stopping(50)], verbose_eval=False)
        pred = (model.predict(X.iloc[va])>0.5).astype(int)
        scores.append(f1_score(y.iloc[va], pred))
    return float(np.mean(scores))

study = optuna.create_study(direction="maximize")
study.optimize(obj, n_trials=n_trials)

out_dir = Path("models/tabular/lightgbm_hpo")
out_dir.mkdir(parents=True, exist_ok=True)
(Path(out_dir/"best_params.json")).write_text(json.dumps(study.best_trial.params, indent=2))

# Retrain on full data (optionally keep fold models)
params = {"objective":"binary","metric":"None","verbose":-1, **study.best_trial.params}
dall = lgb.Dataset(X, label=y)
model = lgb.train(params, dall, num_boost_round=study.best_trial.number+50)
dump(model, out_dir/"model_full.joblib")

# Log to metrics
rep = Path("reports/metrics"); rep.mkdir(parents=True, exist_ok=True)
with (rep/"runs.csv").open("a", encoding="utf-8") as f:
    f.write("run_id,task,model,fold,metric_name,metric_value,split,ts\n") if (rep/"runs.csv").stat().st_size==0 else None
    f.write(f"{int(time.time())},tabular,lightgbm_hpo,all,F1,{study.best_value:.6f},cv,{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")

print("Best F1:", study.best_value)
