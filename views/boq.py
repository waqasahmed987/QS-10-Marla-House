"""Bill of Quantities: MRS vs market vs turnkey + MRS rate build-up (sheets: BOQ, MRS Rate Build-up)."""
import pandas as pd
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, metrics, mn, pct, table

TITLE = "BOQ (MRS vs Market)"
ICON = "📋"


def render(S):
    st.title("Bill of Quantities – MRS 2026 Rawalpindi vs Wah Market")
    b = extract.boq(S)
    items, subs = b["items"], b["subtotals"]
    gt = subs[subs["Section"].str.startswith("GRAND")].iloc[0]
    metrics([("MRS item rates (A)", mn(gt["MRS amount (A)"]), None),
             ("Market composite (B)", mn(gt["Market amount (B)"]), None),
             ("Turnkey (C)", mn(gt["Turnkey amount (C)"]), None),
             ("MRS vs market", pct(gt["% diff"]), None)])
    tabs = st.tabs(["By section", "All items", "Biggest differences", "MRS rate build-up"])
    with tabs[0]:
        sec = subs[~subs["Section"].str.startswith("GRAND")]
        long = sec.melt(id_vars="Section", value_vars=["MRS amount (A)", "Market amount (B)", "Turnkey amount (C)"],
                        var_name="Pricing", value_name="Rs")
        import plotly.express as px
        fig = px.bar(long, x="Section", y="Rs", color="Pricing", barmode="group", color_discrete_sequence=charts.PALETTE,
                     title="Construction cost by section")
        fig.update_yaxes(tickformat=",")
        figure(fig)
        table(subs, pct_cols=("% diff",), label_col="Section")
    with tabs[1]:
        secs = list(dict.fromkeys(items["Section"]))
        sel = st.multiselect("Sections", secs, default=secs)
        q = st.text_input("Search description")
        f = items[items["Section"].isin(sel)]
        if q:
            f = f[f["Description"].astype(str).str.contains(q, case=False)]
        pc = [c for c in f.columns if c.startswith("% Diff")]
        table(f, height=560, pct_cols=pc, label_col="Description")
        download_csv(items, "boq_items.csv")
    with tabs[2]:
        diff_col = [c for c in items.columns if c.startswith("Difference")][0]
        pct_col = [c for c in items.columns if c.startswith("% Diff")][0]
        top = items.reindex(items[diff_col].abs().sort_values(ascending=False).index).head(15)
        fig = charts.go.Figure(charts.go.Bar(y=top["Code"] + " " + top["Description"].str.slice(0, 40), x=top[diff_col],
                                             orientation="h", marker_color=["#C00000" if v > 0 else "#70AD47" for v in top[diff_col]]))
        fig.update_layout(title="Top 15 items: MRS minus market (Rs; red = MRS higher)", **charts.LAYOUT)
        fig.update_yaxes(autorange="reversed")
        figure(fig)
        table(top[["Code", "Description", diff_col, pct_col]], pct_cols=(pct_col,), label_col="Description")
    with tabs[3]:
        st.caption("Each BOQ rate built from the official MRS 2026 schedule items (rate x factor).")
        table(extract.buildup(S), height=600, label_col="MRS item used")
