"""Five-year rate & cost forecast (sheet: 5-Yr Forecast)."""
import pandas as pd
import streamlit as st

from core import charts, extract
from core.ui import figure, table

TITLE = "5-Year Forecast"
ICON = "🔮"


def render(S):
    d = extract.forecast(S)
    st.title("Five-Year Rate & Cost Forecast (2026–2031)")
    proj = d["projection"]
    years = [c for c in proj.columns[1:]]
    tabs = st.tabs(["Projected totals", "Escalation assumptions", "Build now vs wait", "Unit-rate forecast"])
    with tabs[0]:
        scen = st.radio("Scenario", ["Base", "Low", "High"], horizontal=True)
        sub = proj[proj["Option / scenario"].str.endswith(scen)]
        long = sub.melt(id_vars="Option / scenario", value_vars=years, var_name="Year", value_name="Rs")
        import plotly.express as px
        fig = px.line(long, x="Year", y="Rs", color="Option / scenario", markers=True,
                      color_discrete_sequence=charts.PALETTE, title=f"Projected total cost - {scen} scenario")
        fig.update_yaxes(tickformat=",")
        figure(fig)
        table(proj, label_col="Option / scenario")
    with tabs[1]:
        e = d["escalation"]
        table(e, pct_cols=("Low (p.a.)", "Base (p.a.)", "High (p.a.)"), label_col="Cost group")
    with tabs[2]:
        w = d["waiting"]
        table(w, label_col="Item")
        net = w[w["Item"].str.startswith("NET COST")]
        if not net.empty:
            figure(charts.bar_compare(years, list(net.iloc[0][years].values), "Net cost of waiting (Rs)"))
    with tabs[3]:
        u = d["unit_rates"]
        table(u, label_col="Material / rate")
