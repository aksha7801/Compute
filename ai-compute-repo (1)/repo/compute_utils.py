"""Data cleaning and trend calculation for the compute page.

Source: Epoch AI, "Notable AI Models" (CC-BY-4.0)
        https://epoch.ai/data/ai-models
Every step that changes the row count is recorded in `log` so the
number on screen can be traced back to the raw CSV.
"""
import numpy as np
import pandas as pd

DATE_COL = "Publication date"
FLOP_COL = "Training compute (FLOP)"
DOMAIN_COL = "Domain"
MODEL_COL = "Model"
ORG_COL = "Organization"
PARAMS_COL = "Parameters"
COUNTRY_COL = "Country (of organization)"


def clean(raw: pd.DataFrame):
    """Return (clean_df, log). log is a list of (step, rows_remaining)."""
    log = [("Rows in raw CSV", len(raw))]
    df = raw.copy()

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df.dropna(subset=[DATE_COL])
    log.append(("After dropping rows with no usable publication date", len(df)))

    df[FLOP_COL] = pd.to_numeric(df[FLOP_COL], errors="coerce")
    df = df.dropna(subset=[FLOP_COL])
    df = df[df[FLOP_COL] > 0]
    log.append(("After dropping rows with no training compute value", len(df)))

    df["year"] = df[DATE_COL].dt.year + (df[DATE_COL].dt.dayofyear - 1) / 365.25
    df["log10_flop"] = np.log10(df[FLOP_COL])
    return df.reset_index(drop=True), log


def fit_trend(df: pd.DataFrame):
    """Least-squares fit of log10(FLOP) on decimal year.

    Returns dict with slope (orders of magnitude per year), intercept,
    doubling time in months, and n. Returns None if fewer than 3 points
    or all points share the same date.
    """
    if len(df) < 3 or df["year"].nunique() < 2:
        return None
    slope, intercept = np.polyfit(df["year"], df["log10_flop"], 1)
    if slope <= 0:
        return {"slope": slope, "intercept": intercept,
                "doubling_months": None, "n": len(df)}
    doubling_months = 12 * np.log10(2) / slope
    return {"slope": slope, "intercept": intercept,
            "doubling_months": doubling_months, "n": len(df)}
