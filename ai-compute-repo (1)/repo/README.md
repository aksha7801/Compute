# Since 2012, has frontier AI capability grown mainly because training compute was scaled up, or because algorithms improved?

**Question:** Since 2012, has frontier AI capability grown mainly because training compute was scaled up, or because algorithms improved?

**Assessed version:** commit `[PASTE HASH]` / tag `[v1.0]`
**Deployed app:** [PASTE STREAMLIT URL]

## Persona

An **Australian Government funding adviser** who must recommend whether public money should go to compute infrastructure (for example, national GPU capacity) or to algorithmic research. The app helps this adviser judge how fast the compute needed at the frontier is growing, and whether that growth holds across domains and eras, before putting a number into a funding brief.

## User stories

1. As an Australian Government funding adviser, I want to see how the training compute of notable AI models has grown since 2012 and what doubling time that implies, so that I can judge how quickly the compute requirement at the frontier is rising.
   *In the app:* the headline, the main scatter chart, the median-compute-per-year chart and the "doubling time" and "growth per year" tiles.
2. As an Australian Government funding adviser, I want to filter by publication years and domain, so that I can test whether the trend holds for a subset instead of relying on one average across very different eras.
   *In the app:* sidebar year slider and domain selector; all charts and tiles update.
3. As an Australian Government funding adviser, I want to trace the doubling time back to row counts and source rows, so that I can cite the figure in a brief and defend where it came from.
   *In the app:* "Trace the doubling time back to the source data" panel and CSV download.

## Run it

1. Download the **Notable AI Models** CSV from https://epoch.ai/data/ai-models (CC-BY-4.0).
2. Save it as `data/raw/notable_ai_models.csv`.
3. `pip install -r requirements.txt`
4. `python make_data.py` (regenerates everything in `data/processed/`), then optionally `python verify_pipeline.py`
5. `streamlit run app.py`

## Files

- `app.py`: the page (question, headline, filters, seven charts, tiles, stated answer, limits, trace panel, source footer).
- `compute_utils.py`: cleaning and the trend calculation; each cleaning step logs its row count.
- `make_data.py`: regenerates the processed files from the raw sample.
- `verify_pipeline.py`: regenerates the processed files in a temp copy and recomputes key numbers independently from the raw file.
- `data/raw/notable_ai_models.csv`: raw Epoch file, unmodified.
- `data/processed/`: `models_clean.csv`, `cleaning_log.csv`, `coverage_by_year.csv`, `meta.csv` (what the app reads).
- `DATA_DICTIONARY.md`, `PROVENANCE.md`, `DISCLOSURE.md`, `DESIGN_NOTES.md`: data package and process documents.

## How the doubling time is calculated

1. Keep rows with a valid publication date and a positive training compute value.
2. Convert the date to a decimal year and compute log10(FLOP).
3. Fit a least-squares line to log10(FLOP) against year (numpy `polyfit`, degree 1).
4. Doubling time in months = 12 x log10(2) / slope.

## Limits

- The data covers the compute side only. It cannot show how much of the capability gain came from algorithmic efficiency; that needs a separate source.
- One straight line across all models averages over very different eras and domains. Use the filters to test whether the story holds for a subset.
- Epoch's list is of *notable* models, used here as a proxy for the frontier, and compute values are estimates.
- Many recent models have no compute estimate (the app states the share by year), so the newest models are under-represented.
