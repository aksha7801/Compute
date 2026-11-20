"""Regenerate every processed file from the raw sample.  Run: python make_data.py
Input : data/raw/notable_ai_models.csv  (Epoch AI, Notable AI Models, CC-BY-4.0)
Output: data/processed/models_clean.csv, cleaning_log.csv, coverage_by_year.csv, meta.csv
"""
import hashlib
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from compute_utils import (COUNTRY_COL, DATE_COL, DOMAIN_COL, FLOP_COL, MODEL_COL,
                           ORG_COL, PARAMS_COL, clean)

RAW = Path("data/raw/notable_ai_models.csv")
OUT = Path("data/processed")


def main():
    if not RAW.exists():
        sys.exit(f"{RAW} not found. Download it from https://epoch.ai/data/ai-models first.")
    raw = pd.read_csv(RAW)
    missing = [c for c in (DATE_COL, FLOP_COL) if c not in raw.columns]
    if missing:
        sys.exit(f"Missing column(s) {missing}. Columns found: {list(raw.columns)[:15]}")

    df, log = clean(raw)

    # How many notable models per year have a usable compute estimate (computed from the RAW file)
    r = raw.copy()
    r["year"] = pd.to_datetime(r[DATE_COL], errors="coerce").dt.year
    r["has_compute"] = pd.to_numeric(r[FLOP_COL], errors="coerce") > 0
    cov = (r.dropna(subset=["year"]).groupby("year")
             .agg(n_models=("has_compute", "size"), n_with_compute=("has_compute", "sum")).reset_index())
    cov["year"] = cov["year"].astype(int)
    cov["share_with_compute"] = (cov["n_with_compute"] / cov["n_models"]).round(4)
    keep = [c for c in (MODEL_COL, ORG_COL, COUNTRY_COL, DOMAIN_COL, DATE_COL, PARAMS_COL, FLOP_COL, "year", "log10_flop")
            if c in df.columns]
    OUT.mkdir(parents=True, exist_ok=True)
    df[keep].to_csv(OUT / "models_clean.csv", index=False)
    pd.DataFrame(log, columns=["step", "rows"]).to_csv(OUT / "cleaning_log.csv", index=False)
    cov.to_csv(OUT / "coverage_by_year.csv", index=False)
    pd.DataFrame([{
        "raw_file": RAW.name,
        "raw_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "raw_rows": len(raw),
        "clean_rows": len(df),
        "earliest_observation": df[DATE_COL].min().date().isoformat(),
        "latest_observation": df[DATE_COL].max().date().isoformat(),
        "processed_on": date.today().isoformat(),
    }]).to_csv(OUT / "meta.csv", index=False)
    print(f"OK: {len(raw)} raw rows -> {len(df)} clean rows, latest {df[DATE_COL].max():%Y-%m-%d}")


if __name__ == "__main__":
    main()
