import hashlib
import json
from pathlib import Path

import pandas as pd


def main():
    csv_path = Path("data/raw/tabular/data.csv")
    report = {
        "duplicates": [],
        "leaky_paths": [],
    }
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        report["missing_values"] = df.isnull().sum().to_dict()
        seen = {}
        for idx, row in df.iterrows():
            digest = hashlib.md5(str(row.values.tolist()).encode()).hexdigest()
            if digest in seen:
                report["duplicates"].append({"first": seen[digest], "duplicate": idx})
            else:
                seen[digest] = idx
    for path in Path("data/raw/cv").rglob("*"):
        if path.is_file():
            tokens = path.name.lower()
            if any(tok in tokens for tok in ["_pos", "_neg", "class", "label"]):
                report["leaky_paths"].append(str(path))
    out = Path("reports/metrics/leakage_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print("Leakage audit written to", out)


if __name__ == "__main__":
    main()
