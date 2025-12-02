from pathlib import Path
import json

import pandas as pd

REPORTS = Path("reports/metrics")
HIST = REPORTS / "governance_history.json"
OUT = REPORTS / "governance_calibration.csv"

def main():
    if not HIST.exists():
        print("No governance history log found.")
        return
    records = json.loads(HIST.read_text(encoding="utf-8"))
    df = pd.DataFrame(records)
    if df.empty:
        print("History empty.")
        return
    df["risk_score"] = df["risk_score"].astype(float)
    df["incidents"] = df["incidents"].astype(int)
    df["drift_flags"] = df["drift_flags"].astype(int)
    df["calibrated_score"] = df["risk_score"] / (1 + df["incidents"] + df["drift_flags"])
    df.to_csv(OUT, index=False)
    print("Saved governance calibration ->", OUT)

if __name__ == "__main__":
    main()
