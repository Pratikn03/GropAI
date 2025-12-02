from fastapi import APIRouter
from pathlib import Path
import csv, statistics as stats

router = APIRouter()

@router.get("/summary")
def summary():
    runs = Path("reports/metrics/runs.csv")
    lat  = Path("reports/metrics/latency_size.csv")
    out = {"f1": None, "latency_ms": None, "model_size_mb": None}

    try:
        if runs.exists():
            f1_vals=[]
            with runs.open() as f:
                for row in csv.DictReader(f):
                    if row.get("metric_name") == "F1":
                        try: f1_vals.append(float(row.get("metric_value", "nan")))
                        except: pass
            if f1_vals: out["f1"] = round(stats.mean(f1_vals), 4)
    except Exception:
        pass

    try:
        if lat.exists():
            p95=[]; sz=[]
            with lat.open() as f:
                for row in csv.DictReader(f):
                    try:
                        p95.append(float(row.get("p95_ms","nan")))
                        sz.append(float(row.get("size_mb","nan")))
                    except: pass
            if p95: out["latency_ms"] = round(stats.mean(p95), 3)
            if sz:  out["model_size_mb"] = round(stats.mean(sz), 2)
    except Exception:
        pass

    return out
