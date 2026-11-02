"""Option comparison A-D, other costs and owner-supply option (sheets: Summary, Other Costs, Option D)."""
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, metrics, mn, table

TITLE = "Options A–D & Other Costs"
ICON = "⚖️"


def render(S):
    st.title("Procurement Options A–D, Other Costs & Equipment")
    s = extract.summary(S)
    od = extract.option_d(S)
    comp = od["comparison"]
    c0 = comp.columns[0]
    tot = comp[comp[c0].astype(str).str.startswith("TOTAL")].iloc[0]
    opts = list(comp.columns[1:5])
    metrics([(o.split(":")[0], mn(tot[o]), None) for o in opts])
    st.caption("A = item-rate contract at MRS 2026 · B = self-managed at market composite rates · "
               "C = turnkey contractor · D = owner supplies materials, labour-rate contractor, owner hires equipment.")

    tabs = st.tabs(["A–D comparison", "Options A–C detail", "Other costs", "Option D items", "Equipment hire"])
    with tabs[0]:
        figure(charts.bar_compare([o.split(":")[0] for o in opts], [tot[o] for o in opts], "Total cost to owner by option"))
        table(comp, label_col=c0)
    with tabs[1]:
        table(s["costs"], label_col="Cost head")
        st.subheader("Weighted evaluation (A–C)")
        table(s["evaluation"], pct_cols=("Weight",), label_col="Criterion")
        for k, v in s["best"]:
            st.markdown(f"**{k}:** {mn(v) if isinstance(v, (int, float)) else v}")
        st.info(s["recommendation"])
    with tabs[2]:
        oc = extract.other_costs(S)
        phase = st.multiselect("Phase", ["PRE", "CON", "TAX", "UTL", "POST"], default=["PRE", "CON", "TAX", "UTL", "POST"])
        table(oc[oc["Phase"].isin(phase)], height=520, label_col="Item")
        download_csv(oc, "other_costs.csv")
    with tabs[3]:
        it = od["items"]
        table(it, height=520, pct_cols=(it.columns[10],), label_col=it.columns[1])
        download_csv(it, "option_d_items.csv")
    with tabs[4]:
        eq = od["equipment"]
        table(eq, label_col=eq.columns[1])
