"""Independent checks on the data pipeline. Run: python verify_pipeline.py
Each check can fail; the script exits non-zero if any does.
1. Regenerates the processed files in a temp copy and compares them byte-for-byte with the committed ones.
2. Recomputes row counts and the since-2012 doubling time from the RAW csv with plain pandas/numpy
   (not compute_utils) and compares them with the processed files."""
import filecmp, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
fails = []

def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  {detail}" if detail else ""))
    if not ok:
        fails.append(name)

# 1. regeneration
with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp) / "repo"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    for f in (work / "data" / "processed").glob("*.csv"):
        f.unlink()
    subprocess.run([sys.executable, "make_data.py"], cwd=work, check=True, capture_output=True)
    for name in ("models_clean.csv", "cleaning_log.csv", "coverage_by_year.csv"):
        check(f"regenerated {name} identical to committed", filecmp.cmp(work / "data/processed" / name,
                                                                         ROOT / "data/processed" / name, shallow=False))

# 2. independent recomputation from raw
raw = pd.read_csv(ROOT / "data/raw/notable_ai_models.csv")
d = pd.to_datetime(raw["Publication date"], errors="coerce")
f = pd.to_numeric(raw["Training compute (FLOP)"], errors="coerce")
ok_rows = d.notna() & (f > 0)
proc = pd.read_csv(ROOT / "data/processed/models_clean.csv", parse_dates=["Publication date"])
meta = pd.read_csv(ROOT / "data/processed/meta.csv").iloc[0]
check("raw row count matches meta", len(raw) == int(meta["raw_rows"]), f"{len(raw)}")
check("usable row count matches processed file", int(ok_rows.sum()) == len(proc) == int(meta["clean_rows"]), f"{int(ok_rows.sum())}")
yr = d.dt.year + (d.dt.dayofyear - 1) / 365.25
sel = ok_rows & (yr >= 2012)
slope = np.polyfit(yr[sel], np.log10(f[sel]), 1)[0]
p = proc[proc["year"] >= 2012]
slope_p = np.polyfit(p["year"], p["log10_flop"], 1)[0]
check("since-2012 doubling time from raw equals processed", abs(slope - slope_p) < 1e-9,
      f"{12*np.log10(2)/slope:.2f} months, n={int(sel.sum())}")
sys.exit(1 if fails else 0)
