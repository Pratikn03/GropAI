from pathlib import Path
import pandas as pd

INPUT = Path("reports/metrics/governance_history.json")
CALIBRATION = Path("reports/metrics/governance_calibration.csv")
OUTPUT = Path("reports/metrics/governance_correlation.csv")

def main():
    if not INPUT.exists():
        print("Governance history missing.")
        return
    history = pd.read_json(INPUT)
    if history.empty:
        print("Empty history.")
        return
    history["risk_score"] = history["risk_score"].astype(float)
    history["incidents"] = history["incidents"].astype(int)
    history["drift_flags"] = history["drift_flags"].astype(int)
    corr_matrix = history[["risk_score", "incidents", "drift_flags"]].corr(method="spearman")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    corr_matrix.to_csv(OUTPUT)
    print("Saved governance correlation ->", OUTPUT)


if __name__ == "__main__":
    main()
