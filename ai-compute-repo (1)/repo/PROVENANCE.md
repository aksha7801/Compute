# AI provenance matrix

Each member owns at least one row. The "How verified" column names a check that could have failed. Outcomes marked [record] must be filled in by the member after running the check themselves.

| # | Artefact | Who | Tool | What was asked | What came back | How verified (check that could fail) | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | `make_data.py`, `coverage_by_year.csv`, `verify_pipeline.py` | [member] | Claude | Script that regenerates processed files from the raw Epoch CSV, plus an independent check | Python scripts | Ran `python verify_pipeline.py`. It fails if a regenerated file differs from the committed one, or if row counts or the since-2012 doubling time computed from the raw CSV with plain pandas/numpy differ from the processed files | Exited 0 when run by Claude on 20 Nov 2026 (546 usable rows, 5.57 months). [record your own run] |
| 2 | Seven charts, headline, stated answer and limits text in `app.py` | [member] | Claude | Add charts for ranking, change over time, distribution, correlation and geography; state an answer and what the data cannot show | Edited `app.py` | In the running app with default filters, compared on-screen values with pandas on `models_clean.csv`: models shown (400), bars in "models per year" sum to that number, Australian tile equals 3 with all years selected, scatter r matches 0.92. Fails if any filter or year is handled differently | [record] |
| 3 | `README.md`, `DATA_DICTIONARY.md`, `DISCLOSURE.md`, `DESIGN_NOTES.md` | [member] | Claude | Draft the required documents for the compute page | Markdown files | Compared every column and date range in the dictionary with `pd.read_csv(...)` output for each file; fails if a name, count or date is wrong. Walked each user story in the deployed app | [record] |
| 4 | [artefact, e.g. `compute_utils.py` or a chart] | [member 2] | [tool or "none"] | [prompt summary] | [output summary] | [named check that could fail, e.g. hand-computed slope on 5 rows vs `fit_trend`] | [record] |
| 5 | [artefact] | [member 3] | | | | | |
| 6 | [artefact] | [member 4] | | | | | |
