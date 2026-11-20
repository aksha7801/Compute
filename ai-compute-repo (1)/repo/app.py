"""Compute page: has frontier AI capability been driven by scaling training compute?

Run:  streamlit run app.py
Data: Epoch AI "Notable AI Models" CSV (CC-BY-4.0) saved as data/raw/notable_ai_models.csv, then python make_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from compute_utils import (COUNTRY_COL, DATE_COL, DOMAIN_COL, FLOP_COL, MODEL_COL,
                           ORG_COL, PARAMS_COL, fit_trend)

SOURCE_URL = "https://epoch.ai/data/ai-models"
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]  # Okabe-Ito

st.set_page_config(page_title="Compute and capability", layout="wide")
st.markdown("<style>.block-container{padding-top:1.5rem;max-width:100%;}</style>", unsafe_allow_html=True)

QUESTION = ("Since 2012, has frontier AI capability grown mainly because training compute was "
            "scaled up, or because algorithms improved?")
st.title(QUESTION)
st.caption(
    "Persona: an Australian Government funding adviser deciding between funding "
    "compute infrastructure and funding algorithmic research."
)


PROC = Path(__file__).parent / "data" / "processed"


@st.cache_data
def load_processed():
    d = pd.read_csv(PROC / "models_clean.csv", parse_dates=[DATE_COL])
    log = list(pd.read_csv(PROC / "cleaning_log.csv").itertuples(index=False, name=None))
    meta = pd.read_csv(PROC / "meta.csv").iloc[0].to_dict()
    cov = pd.read_csv(PROC / "coverage_by_year.csv")
    return d, log, meta, cov


# ---------------------------------------------------------------- data in
try:
    df, log, meta, cov = load_processed()
except FileNotFoundError:
    st.error("Processed data not found.")
    st.markdown(
        f"Download the **Notable AI Models** CSV from [{SOURCE_URL}]({SOURCE_URL}), save it as "
        "`data/raw/notable_ai_models.csv`, then run `python make_data.py`."
    )
    st.stop()

# ---------------------------------------------------------------- opening headline (whole dataset)
since12 = df[df["year"] >= 2012]
full_fit = fit_trend(since12)
if full_fit and full_fit["doubling_months"]:
    st.success(
        f"**Across all domains, {len(since12):,} notable models published since 2012 show training compute "
        f"doubling about every {full_fit['doubling_months']:.1f} months (roughly "
        f"{10 ** full_fit['slope']:.1f}x per year).** "
        f"Of {int(meta['raw_rows']):,} models in Epoch's notable list, {int(meta['clean_rows']):,} have a "
        "compute estimate and can be used. Fitted on log10 training compute (FLOP) against publication "
        "date. The filters below change the selection."
    )

# ---------------------------------------------------------------- filters
st.sidebar.header("Filters")
ymin, ymax = int(df["year"].min()), int(df["year"].max()) + 1
default_start = max(2012, ymin)
year_range = st.sidebar.slider("Publication years", ymin, ymax, (default_start, ymax))

if DOMAIN_COL in df.columns:
    # A model can list several domains separated by commas; keep the first listed.
    df["domain_main"] = df[DOMAIN_COL].fillna("Unspecified").astype(str).str.split(",").str[0].str.strip()
    counts = df["domain_main"].value_counts()
    options = list(counts.index)
    chosen = st.sidebar.multiselect("Domain", options, default=options[:4] if len(options) > 4 else options,
                                    help="Defaults to the four domains with the most models. Up to seven can be chosen.",
                                    max_selections=7)
else:
    df["domain_main"] = "All"
    chosen = ["All"]

# Colours are fixed to the seven most common domains so they never repeat; rarer domains are grey.
rank = list(df["domain_main"].value_counts().index)
color_map = {d: (PALETTE[rank.index(d)] if rank.index(d) < len(PALETTE) else "#7F7F7F") for d in rank}
show_trend = st.sidebar.checkbox("Show fitted trend line", value=True)

view = df[(df["year"] >= year_range[0]) & (df["year"] < year_range[1])
          & (df["domain_main"].isin(chosen))]

if view.empty:
    st.warning("No models match these filters.")
    st.stop()

fit = fit_trend(view)

# ---------------------------------------------------------------- tiles
c1, c2, c3 = st.columns(3)
c1.metric("Models shown", f"{len(view):,}")
if fit and fit["doubling_months"]:
    c2.metric("Training compute doubling time", f"{fit['doubling_months']:.1f} months")
    c3.metric("Growth per year", f"{10 ** fit['slope']:.1f}x")
else:
    c2.metric("Training compute doubling time", "n/a")
    c3.metric("Growth per year", "n/a")
    st.info("Not enough points, or no upward trend, in this selection to fit a line.")

# ---------------------------------------------------------------- answer and limits
c21 = cov[cov["year"] == 2021]
c_last = cov[cov["year"] == cov["year"].max()]
if len(c21) and len(c_last):
    coverage_note = (f"(5) compute estimates are missing for many recent models: "
                     f"{c21['share_with_compute'].iloc[0]:.0%} of notable models published in 2021 have one, against "
                     f"{c_last['share_with_compute'].iloc[0]:.0%} in {int(c_last['year'].iloc[0])} so far, so the newest models are "
                     "under-represented; ")
else:
    coverage_note = ""
st.markdown("### Our answer")
st.markdown(
    "**Compute used by notable models has grown very fast, but this data cannot show that compute was "
    "the main driver of capability.** Training compute grew exponentially over the period shown (see the "
    "doubling time above, for the years and domains selected). The data has no capability measure and no "
    "measure of algorithmic progress, so a reasonable reader using the same data could still argue that "
    "algorithmic research deserves the funding."
)
st.warning(
    "**What this data cannot show:** (1) how much capability improved per model, because the data has "
    "no benchmark scores; (2) how much of any gain came from better algorithms rather than more compute; "
    "(3) models outside Epoch's notable list, which is used here as a proxy for the frontier; "
    "(4) exact compute, since values are Epoch estimates; " + coverage_note +
    "The fitted trend is a descriptive straight line on a log scale, not a forecast."
)
st.caption(
    f"Baseline for every figure above: models in the selected years and domains ({len(view):,} models, "
    f"{view[DATE_COL].min():%b %Y} to {view[DATE_COL].max():%b %Y}). Compute is in FLOP; "
    "doubling time is in months; growth is a multiple per year."
)

# ---------------------------------------------------------------- chart
fig = go.Figure()
for dom, g in view.groupby("domain_main"):
    hover = g[MODEL_COL].astype(str) if MODEL_COL in g.columns else g.index.astype(str)
    org = g[ORG_COL].astype(str) if ORG_COL in g.columns else ""
    fig.add_trace(go.Scatter(
        x=g[DATE_COL], y=g[FLOP_COL], mode="markers", name=dom,
        marker=dict(size=7, opacity=0.75, color=color_map[dom]),
        customdata=np.column_stack([hover, org]),
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                      "%{x|%b %Y}<br>%{y:.2e} FLOP<extra></extra>"))

if show_trend and fit:
    xs = np.linspace(view["year"].min(), view["year"].max(), 50)
    ys = 10 ** (fit["intercept"] + fit["slope"] * xs)
    # decimal year -> datetime
    dates =pd.to_datetime("1970-01-01") + pd.to_timedelta((xs - 1970) * 365.25, unit="D")
    fig.add_trace(go.Scatter(x=dates, y=ys, mode="lines", name="Fitted trend (all shown models)",
                             line=dict(color="black", width=2, dash="dash"), hoverinfo="skip"))

top5 = view.nlargest(5, FLOP_COL)
names5 = top5[MODEL_COL].astype(str) if MODEL_COL in top5.columns else top5.index.astype(str)
fig.add_trace(go.Scatter(
    x=top5[DATE_COL], y=top5[FLOP_COL], mode="markers+text", name="Five largest (labelled)",
    text=[f"{n}: {v:.1e}" for n, v in zip(names5, top5[FLOP_COL])], textposition="middle left",
    marker=dict(size=10, color="black", symbol="diamond-open"), hoverinfo="skip"))
if show_trend and fit and fit["doubling_months"]:
    fig.add_annotation(x=dates[-1], y=np.log10(ys[-1]), text=f"Trend: doubles every {fit['doubling_months']:.1f} months",
                       showarrow=True, ax=-120, ay=-30, yref="y", font=dict(size=12))
fig.update_yaxes(type="log", title="Training compute (FLOP), log scale")
fig.update_xaxes(title="Publication date")
fig.update_layout(title="Training compute of notable AI models over time (one dot = one model)",
                  height=440, margin=dict(l=10, r=10, t=50, b=10),
                  legend=dict(orientation="h", y=-0.2, title_text="Domain"))
st.plotly_chart(fig, width="stretch")
st.caption(
    "Log axis: a straight line means constant exponential growth, and its slope sets the doubling time. "
    "This page shows the compute side only. Algorithmic efficiency needs its own source and is not "
    "estimated here."
)


# ---------------------------------------------------------------- more charts
st.subheader("Context for the compute trend")
view = view.assign(pub_year=view[DATE_COL].dt.year)
BASE = dict(height=380, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
left, right = st.columns(2)

# Change over time: how many models per year
per_year = view.groupby("pub_year").size().reset_index(name="n")
fig2 = go.Figure(go.Bar(x=per_year["pub_year"], y=per_year["n"], text=per_year["n"],
                        textposition="outside", marker_color=PALETTE[0]))
fig2.update_layout(title="Notable models published per year", **BASE)
fig2.update_xaxes(title="Publication year", dtick=1)
fig2.update_yaxes(title="Number of models", rangemode="tozero")
left.plotly_chart(fig2, width="stretch")
left.caption("Counts only models in Epoch's notable list for the selected years and domains; "
             "it is not a count of all AI models.")

# Ranking: which organisations published the most
if ORG_COL in view.columns:
    lead = view[ORG_COL].fillna("Unspecified").astype(str).str.split(",").str[0].str.strip()
    top = lead.value_counts().head(10).sort_values()
    fig3 = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h", text=top.values,
                            textposition="outside", marker_color=PALETTE[1]))
    fig3.update_layout(title="Top 10 organisations by number of notable models", **BASE)
    fig3.update_xaxes(title="Number of models", rangemode="tozero")
    fig3.update_yaxes(title="Lead organisation")
    right.plotly_chart(fig3, width="stretch")
    right.caption("Lead organisation = first one listed when a model has several.")

# Distribution: models by order of magnitude of training compute
mag = np.floor(view["log10_flop"]).astype(int).value_counts().sort_index()
fig4 = go.Figure(go.Bar(x=[f"1e{k}" for k in mag.index], y=mag.values, text=mag.values,
                        textposition="outside", marker_color=PALETTE[2]))
fig4.update_layout(title="Models by order of magnitude of training compute", **BASE)
fig4.update_xaxes(title="Training compute (FLOP, lower bound of each power of ten)")
fig4.update_yaxes(title="Number of models", rangemode="tozero")
left2, right2 = st.columns(2)
left2.plotly_chart(fig4, width="stretch")
right2.markdown("**Ten largest training runs in the selection (values readable without hovering)**")
tcols = [c for c in (MODEL_COL, ORG_COL, DATE_COL, FLOP_COL) if c in view.columns]
tbl = view.nlargest(10, FLOP_COL)[tcols].copy()
tbl[DATE_COL] = tbl[DATE_COL].dt.strftime("%b %Y")
tbl[FLOP_COL] = tbl[FLOP_COL].map("{:.2e}".format)
tbl = tbl.rename(columns={FLOP_COL: "Training compute (FLOP)"})
right2.dataframe(tbl, hide_index=True, width="stretch", height=340)

# ---------------------------------------------------------------- more views
st.subheader("More views: size, typical compute and geography")
a, b = st.columns(2)

# Correlation: parameters vs training compute
pv = view.assign(params=pd.to_numeric(view[PARAMS_COL], errors="coerce")) if PARAMS_COL in view.columns else None
if pv is not None:
    pv = pv[pv["params"] > 0]
if pv is not None and len(pv) >= 3:
    fig5 = go.Figure()
    for dom, g in pv.groupby("domain_main"):
        fig5.add_trace(go.Scatter(x=g["params"], y=g[FLOP_COL], mode="markers", name=dom,
                                  marker=dict(size=6, opacity=0.75, color=color_map[dom]),
                                  hovertext=g[MODEL_COL].astype(str) if MODEL_COL in g.columns else None,
                                  hovertemplate="<b>%{hovertext}</b><br>%{x:.2e} parameters<br>%{y:.2e} FLOP<extra></extra>"))
    big = pv.nlargest(3, FLOP_COL)
    fig5.add_trace(go.Scatter(x=big["params"], y=big[FLOP_COL], mode="markers+text", name="Three largest runs",
                              text=big[MODEL_COL].astype(str), textposition="middle left",
                              marker=dict(size=10, color="black", symbol="diamond-open"), hoverinfo="skip"))
    fig5.update_xaxes(type="log", title="Parameters (count, log scale)")
    fig5.update_yaxes(type="log", title="Training compute (FLOP, log scale)")
    fig5.update_layout(title="Model size vs training compute (one dot = one model)",
                       height=400, margin=dict(l=10, r=10, t=50, b=10),
                       legend=dict(orientation="h", y=-0.25, title_text="Domain"))
    r = np.corrcoef(np.log10(pv["params"]), pv["log10_flop"])[0, 1]
    a.plotly_chart(fig5, width="stretch")
    a.caption(f"{len(pv):,} models with both values. Correlation of log10 values: r = {r:.2f}. "
              "Compute estimates are partly derived from parameter counts, so the two are not independent.")
else:
    a.info("Not enough models with a parameter count in this selection.")

# Change over time: median compute per year, labelled
med = view.groupby("pub_year")[FLOP_COL].median().reset_index()
fig6 = go.Figure(go.Scatter(x=med["pub_year"], y=med[FLOP_COL], mode="lines+markers+text",
                            text=[f"{v:.1e}" for v in med[FLOP_COL]], textposition="top center",
                            line=dict(color=PALETTE[3]), marker=dict(size=7, color=PALETTE[3])))
fig6.update_xaxes(title="Publication year", dtick=2)
fig6.update_yaxes(type="log", title="Median training compute (FLOP, log scale)")
fig6.update_layout(title="Median training compute of models published each year",
                   height=400, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
b.plotly_chart(fig6, width="stretch")
b.caption("Median of models with a compute estimate. Years with few models are noisy; see the count chart above.")

# Ranking: countries
if COUNTRY_COL in view.columns:
    c1, c2 = st.columns(2)
    ctry = view[COUNTRY_COL].fillna("Unspecified").astype(str).str.split(",").str[0].str.strip()
    topc = ctry.value_counts().head(8).sort_values()
    fig7 = go.Figure(go.Bar(x=topc.values, y=topc.index, orientation="h", text=topc.values,
                            textposition="outside", marker_color=PALETTE[5]))
    fig7.update_xaxes(title="Number of models", rangemode="tozero")
    fig7.update_yaxes(title="Country of lead organisation", automargin=True)
    fig7.update_layout(title="Top 8 countries by number of notable models",
                       height=380, margin=dict(l=10, r=40, t=50, b=10), showlegend=False)
    c1.plotly_chart(fig7, width="stretch")
    au = int(view[COUNTRY_COL].fillna("").astype(str).str.contains("Australia").sum())
    c2.metric("Models with an Australian organisation (current selection)", au)
    c2.caption("Counts a model if Australia appears among its listed organisation countries. "
               "Only models with a compute estimate are included, so this understates Australian activity.")


# ---------------------------------------------------------------- footer
st.caption(f"Source: Epoch AI, Notable AI Models, {SOURCE_URL} (CC-BY-4.0). "
           f"Latest model in selection: {view[DATE_COL].max():%b %Y}. Data last processed: {meta['processed_on']}; latest model with a compute estimate: {meta['latest_observation']}.")

# ---------------------------------------------------------------- trace
with st.expander("Trace the doubling time back to the source data", expanded=False):
    st.markdown(f"**Source:** Epoch AI, Notable AI Models, [{SOURCE_URL}]({SOURCE_URL}) (CC-BY-4.0).")
    st.markdown("**Cleaning steps (row counts):**")
    steps = pd.DataFrame(log, columns=["Step", "Rows"])
    steps.loc[len(steps)] = ["After year and domain filters (what is plotted)", len(view)]
    st.dataframe(steps, hide_index=True, width="stretch")
    if fit:
        st.markdown(
            "**Method:** least-squares line through log10(Training compute in FLOP) against decimal "
            "publication year, using the rows plotted.  \n"
            f"slope = {fit['slope']:.4f} orders of magnitude per year  \n"
            "doubling time (months) = 12 × log10(2) / slope = "
            f"12 × 0.3010 / {fit['slope']:.4f} = **{fit['doubling_months']:.1f}**"
            if fit["doubling_months"] else "Slope is not positive, so there is no doubling time."
        )
    st.markdown("**Five most recent plotted rows, from the processed file:**")
    cols = [c for c in (MODEL_COL, ORG_COL, DATE_COL, FLOP_COL) if c in view.columns]
    st.dataframe(view.sort_values(DATE_COL, ascending=False)[cols].head(5),
                 hide_index=True, width="stretch")
    st.download_button("Download plotted rows (CSV)",
                       view[[c for c in (MODEL_COL, ORG_COL, DOMAIN_COL, DATE_COL, FLOP_COL) if c in view.columns]]
                       .to_csv(index=False), "plotted_rows.csv", "text/csv")
