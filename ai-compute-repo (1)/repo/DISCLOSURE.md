# Data and AI disclosure statement

**Data.** The only data source is Epoch AI's "Notable AI Models" dataset (https://epoch.ai/data/ai-models-documentation), used under CC BY 4.0 and downloaded on 20 Nov 2026. The raw file is stored unmodified in `data/raw/`. Every figure on screen is computed from it by `make_data.py`, `compute_utils.py` and `app.py`, as documented in `DATA_DICTIONARY.md`.

**AI use.** The group used Claude (Anthropic) to draft and edit the Streamlit code and data scripts, add charts, write the on-screen answer and limits text, and draft the README, data dictionary and design notes. Each use is listed in `PROVENANCE.md` with who did it, what was asked, what came back and how it was checked. [Add any other tools used, e.g. GitHub Copilot, or delete this sentence.]

**What AI did not do.** AI did not supply or alter any data values: the raw file was downloaded by a group member and is unmodified. [Edit to match what really happened, e.g. who chose the question and persona, and who checked the numbers.]

**Limits.** Epoch's list covers notable models, not all models, and compute values are estimates. Many recent models have no compute estimate and are excluded, so the newest models are under-represented. The data covers the compute side of the question only and cannot separate algorithmic progress from scale. Fitted doubling times are descriptive and depend on the years and domains selected.
