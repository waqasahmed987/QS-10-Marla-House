"""10 kW on-grid solar system: cost build-up, O&M and payback (sheet: Solar System)."""
import streamlit as st

from core import charts, extract
from core.ui import figure, metrics, mn, note, pct, rs, table

TITLE = "Solar System"
ICON = "☀️"


def render(S):
    d = extract.solar(S)
    st.title("Solar System – 10 kW On-grid (Net Billing)")
    note(d["note"])
    s = dict(d["summary"])
    keys = list(s.keys())
    pb = {k: v for k, v in d["payback"] if isinstance(v, (int, float))}
    metrics([
        ("Installed cost", rs(s[keys[0]]), None),
        ("First-year O&M", rs(s[keys[1]]), None),
        ("Share of route (b) total", pct(s[keys[3]]), None),
        ("Simple payback", f"{list(pb.values())[0]:.1f} years" if pb else "-", None),
    ])
    tabs = st.tabs(["Cost build-up", "Savings & payback", "Design inputs", "Share of project cost"])
    with tabs[0]:
        b = d["build"]
        stages = b[b[b.columns[0]].astype(str).str.startswith("Sub-total Stage")]
        figure(charts.pie(stages[b.columns[0]], stages[b.columns[4]], "Installed cost by stage"))
        table(b, label_col=b.columns[0])
        st.subheader("First-year operation & maintenance")
        table(d["om"], label_col=d["om"].columns[0])
    with tabs[1]:
        sv = d["savings"]
        years = [c for c in sv.columns[1:6]]
        net = sv[sv["Year"] == "Net saving (Rs)"]
        cum = sv[sv["Year"] == "Cumulative net saving (Rs)"]
        if not net.empty:
            fig = charts.go.Figure()
            fig.add_trace(charts.go.Bar(x=years, y=net.iloc[0][years].values, name="Net saving", marker_color="#70AD47"))
            if not cum.empty:
                fig.add_trace(charts.go.Scatter(x=years, y=cum.iloc[0][years].values, name="Cumulative", mode="lines+markers",
                                                line=dict(color="#1F3864")))
            fig.add_hline(y=s[keys[0]], line_dash="dot", annotation_text="Installed cost")
            fig.update_layout(title="Yearly and cumulative net saving (Rs)", **charts.LAYOUT)
            fig.update_yaxes(tickformat=",")
            figure(fig)
        table(sv, label_col="Year")
        for k, v in d["payback"]:
            st.markdown(f"**{k}:** {rs(v) if isinstance(v, (int, float)) and abs(v) > 100 else (f'{v:.1f}' if isinstance(v, float) else '')}"
                        if v is not None else f"_{k}_")
    with tabs[2]:
        table(d["inputs"], label_col="Parameter", pct_rows_contain=("share", "escalation", "degradation"))
    with tabs[3]:
        for k, v in d["summary"][3:]:
            st.markdown(f"- {k}: **{pct(v)}**")
