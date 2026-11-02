"""Responsibility matrix - all parties, pre-construction to handover (sheet: Responsibility Matrix)."""
import pandas as pd
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, note, table

TITLE = "Responsibility Matrix"
ICON = "🤝"


def render(S):
    d = extract.matrix(S)
    st.title("Responsibility Matrix – Pre-construction to Handover")
    note(d["note"])
    mat, parties = d["matrix"], d["parties"]
    lead_col = [c for c in mat.columns if c.startswith("Lead")][0]

    counts = pd.DataFrame({"Party": parties,
                           "Involved": [(mat[p] == "✓").sum() for p in parties],
                           "Leads": [(mat[lead_col] == p).sum() for p in parties]})
    tabs = st.tabs(["Matrix", "By party", "Activity details", "Party roles"])
    with tabs[0]:
        phases = list(dict.fromkeys(mat["Phase"]))
        sel = st.multiselect("Phases", phases, default=phases)
        show = st.multiselect("Parties (columns)", parties, default=parties)
        cols = ["No.", "Activity / work"] + show + [lead_col]
        f = mat[mat["Phase"].isin(sel)][cols]
        table(f, height=620, raw=True)
        download_csv(mat, "responsibility_matrix.csv")
    with tabs[1]:
        long = counts.melt(id_vars="Party", var_name="Count", value_name="Activities")
        import plotly.express as px
        fig = px.bar(long, x="Activities", y="Party", color="Count", barmode="group", orientation="h",
                     color_discrete_sequence=["#4472C4", "#70AD47"], title="Activities involved / led per party")
        fig.update_yaxes(autorange="reversed")
        figure(fig)
        party = st.selectbox("Show activities for", parties, index=0)
        mine = mat[mat[party] == "✓"][["Phase", "No.", "Activity / work", lead_col]]
        mine = mine.assign(Role=["LEAD" if l == party else "Involved" for l in mine[lead_col]])
        table(mine, raw=True)
    with tabs[2]:
        detail_cols = [c for c in mat.columns if c not in parties]
        table(mat[detail_cols], height=620, raw=True)
    with tabs[3]:
        table(d["roles"], raw=True)
