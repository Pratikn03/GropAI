from pathlib import Path
import pandas as pd

INPUT = Path("reports/privacy_utility/blur_sweep.csv")
OUTPUT = Path("reports/privacy_utility/pu_auc.csv")

def main():
    if not INPUT.exists():
        print("Blur sweep missing.")
        return
    df = pd.read_csv(INPUT).sort_values("utility")
    df["priv"] = df["privacy"]
    df["utility_norm"] = (df["utility"] - df["utility"].min()) / (df["utility"].max() - df["utility"].min() + 1e-9)
    df["priv_norm"] = (df["priv"] - df["priv"].min()) / (df["priv"].max() - df["priv"].min() + 1e-9)
    auc = (df["utility_norm"] * df["priv_norm"]).mean()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"pu_auc": [auc]}).to_csv(OUTPUT, index=False)
    print("Saved PU-AUC ->", OUTPUT)


if __name__ == "__main__":
    main()
