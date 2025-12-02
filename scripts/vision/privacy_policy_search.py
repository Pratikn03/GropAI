from pathlib import Path

import pandas as pd

DATA = Path("reports/privacy_utility/blur_sweep.csv")
OUT = Path("reports/privacy_utility/policy_search.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

def run(target_map=0.5):
    if not DATA.exists():
        print("Run blur_sweep first.")
        return
    df = pd.read_csv(DATA)
    df["identifiability"] = 1 - df["privacy"]
    candidates = []
    for _, row in df.iterrows():
        if row["utility"] >= target_map:
            candidates.append(row)
    if not candidates:
        print("No kernels meet utility target.")
        return
    best = min(candidates, key=lambda r: r["identifiability"])
    df["policy"] = df.apply(lambda r: "selected" if r["kernel"]==best["kernel"] else "fixed", axis=1)
    df.to_csv(OUT, index=False)
    print("Policy search done ->", OUT)

if __name__=="__main__":
    run()
