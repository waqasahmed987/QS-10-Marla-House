"""Project assumptions and basic material/labour rates (sheets: Assumptions, Material Rates)."""
import streamlit as st

from core import charts, extract
from core.ui import figure, table

TITLE = "Assumptions & Material Rates"
ICON = "🧱"


def render(S):
    st.title("Project Assumptions & Basic Rates")
    t1, t2 = st.tabs(["Assumptions", "Material & labour rates"])
    with t1:
        a = extract.assumptions(S)
        st.caption("Change these in the Excel file (sheet 'Assumptions', blue cells) and upload the saved file in the sidebar.")
        table(a, label_col="Parameter",
              pct_rows_contain=("%", "rate", "share", "Punjab sales tax", "overhead", "increase", "Withholding"))
    with t2:
        m = extract.materials(S)
        table(m, pct_cols=("% Difference",), label_col="Item")
        body = m[m["Item"].notna()]
        fig = charts.go.Figure()
        fig.add_trace(charts.go.Bar(x=body["Item"], y=body["% Difference"], marker_color="#4472C4"))
        fig.update_layout(title="MRS basic rate vs Wah market (%; negative = market higher)", **charts.LAYOUT)
        fig.update_yaxes(tickformat=".0%")
        figure(fig)
