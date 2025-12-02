from pathlib import Path
import hashlib, csv

roots = [Path("data/shards/cv"), Path("data/shards/audio"), Path("data/shards/text")]
out = Path("data/metadata/manifests"); out.mkdir(parents=True, exist_ok=True)
manifest = out/"shards_manifest.csv"

rows=[]
for root in roots:
    if not root.exists(): 
        continue
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h = hashlib.sha256()
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(1<<20), b""):
                    h.update(chunk)
            rows.append({"path": str(p), "sha256": h.hexdigest(), "bytes": p.stat().st_size})

with manifest.open("w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=["path","sha256","bytes"])
    wr.writeheader()
    wr.writerows(rows)

print("Wrote", manifest, "rows:", len(rows))
