from pathlib import Path
import json, re, hashlib

report = {"duplicates": [], "label_in_path": []}

# 1) Duplicate file content across shards
seen = {}
for p in Path("data/shards").rglob("*"):
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h in seen:
            report["duplicates"].append({"a": seen[h], "b": str(p)})
        else:
            seen[h] = str(p)

# 2) Label tokens in file paths (very naive)
label_tokens = {"positive","negative","fraud","benign","class0","class1"}
for p in Path("data/shards").rglob("*"):
    s = str(p).lower()
    if any(tok in s for tok in label_tokens):
        report["label_in_path"].append(str(p))

Path("data/metadata/verify_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("Leakage report → data/metadata/verify_report.json")
