# Data dictionary

Every file below is read by the app, or by `make_data.py` to produce what the app reads. All derived files are built from dataset 1 only, so they inherit its source, URL and licence.

## 1. data/raw/notable_ai_models.csv (raw sample, unmodified)
| Field | Detail |
|---|---|
| Source | Epoch AI, "Notable AI Models" (AI models dataset, notable subset) |
| URL | https://epoch.ai/data/notable_ai_models.csv (documentation: https://epoch.ai/data/ai-models-documentation) |
| Licence | Creative Commons Attribution 4.0 (CC BY 4.0), credit Epoch AI |
| Date downloaded | 20 Nov 2026 |
| Columns and units | 47 columns, 1,102 rows. The ones the app uses: `Model` (text); `Organization` (text, may list several, comma separated); `Country (of organization)` (text, may list several); `Domain` (text, may list several); `Publication date` (YYYY-MM-DD); `Parameters` (count, blank for many models); `Training compute (FLOP)` (floating-point operations, Epoch estimate, blank for 556 rows). All other columns are ignored. |
| Primary key | `Model` (checked: all 1,102 values are unique) |
| Time coverage | 1950-07-02 to 2026-11-10 |
| Latest observation | 2026-11-10 |
| Transform | None. Saved exactly as downloaded. |

## 2. data/processed/models_clean.csv (read by the app)
| Field | Detail |
|---|---|
| Source | Dataset 1, via `make_data.py` and `compute_utils.clean` |
| URL / licence | As dataset 1 (https://epoch.ai/data/notable_ai_models.csv; CC BY 4.0, adapted by the group) |
| Columns and units | `Model` (text); `Organization` (text); `Country (of organization)` (text); `Domain` (text); `Publication date` (YYYY-MM-DD); `Parameters` (count, blank if unknown); `Training compute (FLOP)` (FLOP); `year` (decimal year = year + (day of year - 1) / 365.25); `log10_flop` (log10 of training compute, no unit) |
| Primary key | `Model` |
| Time coverage | 1950-07-02 to 2026-11-05 (546 rows) |
| Latest observation | 2026-11-05 (latest publication date among rows with a compute estimate) |
| Transform | (a) parse `Publication date`, drop rows that fail; (b) coerce `Training compute (FLOP)` to a number, drop rows with no value or value <= 0; (c) add `year` and `log10_flop`; (d) keep only the columns listed above |

## 3. data/processed/cleaning_log.csv (read by the app's trace panel)
| Field | Detail |
|---|---|
| Source / URL / licence | Dataset 1 via `make_data.py`; as dataset 1 |
| Columns and units | `step` (text); `rows` (count of rows remaining after that step) |
| Primary key | `step` |
| Time coverage | Not a time series; describes the whole raw file (1950-07-02 to 2026-11-10) |
| Latest observation | 2026-11-10 (latest date in the raw file it was built from) |
| Transform | One row per step of `compute_utils.clean`: raw rows (1,102), after date filter (1,102), after compute filter (546) |

## 4. data/processed/coverage_by_year.csv (read by the app's limits text)
| Field | Detail |
|---|---|
| Source / URL / licence | Dataset 1 via `make_data.py`; as dataset 1 |
| Columns and units | `year` (calendar year); `n_models` (count of notable models in the raw file); `n_with_compute` (count with Training compute > 0); `share_with_compute` (0 to 1) |
| Primary key | `year` |
| Time coverage | 1950 to 2026 (2026 is a partial year) |
| Latest observation | 2026 (models published up to 2026-11-10) |
| Transform | Parse the raw `Publication date` to a year; count all rows and rows with a positive compute value per year; divide |

## 5. data/processed/meta.csv (read by the app's footer and headline)
| Field | Detail |
|---|---|
| Source / URL / licence | Dataset 1 via `make_data.py`; as dataset 1 |
| Columns and units | `raw_file` (text); `raw_sha256` (hash of the raw file); `raw_rows`, `clean_rows` (counts); `earliest_observation`, `latest_observation` (YYYY-MM-DD, among rows with a compute estimate); `processed_on` (YYYY-MM-DD) |
| Primary key | `raw_file` (one row) |
| Time coverage | 1950-07-02 to 2026-11-05 |
| Latest observation | 2026-11-05 |
| Transform | Hash the raw file; count rows before and after cleaning; take min and max of `Publication date` in the cleaned data; record the run date. `processed_on` changes each time `make_data.py` runs, so this file is the only one that differs between regenerations. |

## Derived values shown on screen
| Value | Transform |
|---|---|
| Models shown | Count of `models_clean.csv` rows in the chosen years and domains |
| Headline doubling time and growth | As below, on all rows since 2012, all domains |
| Growth per year (x) | 10 ^ slope; slope is the least-squares fit of `log10_flop` on `year` (orders of magnitude per year) |
| Doubling time (months) | 12 x log10(2) / slope |
| Domain used for filtering and colours | First domain listed in `Domain`, trimmed |
| Lead organisation / lead country | First value listed in `Organization` / `Country (of organization)`, trimmed |
| Models per year | Count of rows by calendar year of `Publication date` |
| Models per order of magnitude | Count of rows by floor(`log10_flop`) |
| Median compute per year | Median of `Training compute (FLOP)` by calendar year |
| Parameters vs compute correlation (r) | Pearson correlation of log10(`Parameters`) and `log10_flop`, rows with `Parameters` > 0 |
| Australian models | Count of rows whose `Country (of organization)` contains "Australia" |
| Share of models with a compute estimate | `share_with_compute` for 2021 and for the latest year in `coverage_by_year.csv` |

## Regeneration
`python make_data.py` rebuilds datasets 2 to 5 from dataset 1. `python verify_pipeline.py` regenerates them in a temporary copy, compares them with the committed files, and recomputes the row counts and the since-2012 doubling time independently from the raw file.
