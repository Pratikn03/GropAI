from pathlib import Path

import numpy as np
import pandas as pd

OLD = Path("data/metadata/splits/old.csv")
NEW = Path("data/raw/tabular/data.csv")
OUT = Path("reports/metrics/psi_ks.csv")

def psi(old_col, new_col, bins=10):
    def _bin(array):
        return np.histogram(array, bins=bins, density=True)[0]
    old_dist = _bin(old_col)
    new_dist = _bin(new_col)
    old_dist += 1e-8
    new_dist += 1e-8
    psi_val = np.sum((old_dist - new_dist) * np.log(old_dist / new_dist))
    return psi_val

def ks_stat(old_col, new_col):
    return np.max(np.abs(np.sort(old_col) - np.sort(new_col)))

def main():
    if not OLD.exists() or not NEW.exists():
        print("Need old and new data for PSI/KS.")
        return
    old_df = pd.read_csv(OLD)
    new_df = pd.read_csv(NEW)
    numeric_cols = old_df.select_dtypes(include="number").columns.intersection(new_df.columns)
    rows = []
    for col in numeric_cols:
        psi_val = psi(old_df[col].values, new_df[col].values)
        ks_val = ks_stat(old_df[col].values, new_df[col].values)
        rows.append({"feature": col, "psi": psi_val, "ks": ks_val})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("Saved PSI/KS ->", OUT)

if __name__ == "__main__":
    main()
