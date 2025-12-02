import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "metrics"

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def write_flag(name):
    REPORTS.mkdir(parents=True, exist_ok=True)
    flag = REPORTS / f"{name}.txt"
    flag.write_text(f"{name} run", encoding="utf-8")


def main():
    splits_dir = ROOT / "benchmarks" / "leakbench_mm" / "splits"
    safe = splits_dir / "safe_kfold.json"
    leaky = splits_dir / "leaky_kfold.json"
    target_split = ROOT / "data" / "metadata" / "splits" / "kfold.json"
    target_split.parent.mkdir(parents=True, exist_ok=True)

    target_split.write_text(leaky.read_text(), encoding="utf-8")
    run([sys.executable, "scripts/tabular/hpo_lightgbm_optuna.py", "configs/tabular/lightgbm_hpo.yml"])
    write_flag("leaky_run")

    target_split.write_text(safe.read_text(), encoding="utf-8")
    run([sys.executable, "scripts/tabular/hpo_lightgbm_optuna.py", "configs/tabular/lightgbm_hpo.yml"])
    write_flag("safe_run")
    print("LeakBench-MM benchmark skeleton complete.")


if __name__ == "__main__":
    main()
