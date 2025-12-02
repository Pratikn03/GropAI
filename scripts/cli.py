import argparse
import subprocess

CMDS = {
    "hpo": ["python", "scripts/tabular/hpo_lightgbm_optuna.py", "configs/tabular/lightgbm_hpo.yml"],
    "shap": ["python", "scripts/tabular/shap_report.py"],
    "rag": ["python", "scripts/rag/build_ann.py"],
    "leak": ["python", "scripts/tabular/leakage_audit.py"],
    "eval": ["python", "scripts/tabular/eval_report.py"],
    "ops": ["python", "scripts/ops/measure_latency.py"],
}


def main():
    parser = argparse.ArgumentParser(description="Run project subsystems")
    parser.add_argument("cmd", choices=CMDS.keys())
    args = parser.parse_args()
    subprocess.run(CMDS[args.cmd], check=True)


if __name__ == "__main__":
    main()
