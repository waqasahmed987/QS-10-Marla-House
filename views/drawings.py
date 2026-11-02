"""Drawing register: approval, IFC, shop, finishing and as-built drawings (sheet: Drawing Register)."""
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, metrics, note, table

TITLE = "Drawing Register"
ICON = "📐"


def render(S):
    d = extract.drawings(S)
    st.title("Drawing Register")
    note(d["note"])
    reg, summ = d["register"], d["summary"]
    tot = summ[summ["Section"].astype(str).str.startswith("TOTAL")]
    approved = tot.iloc[0]["Approved / IFC"] if not tot.empty else 0
    metrics([("Total drawings", str(len(reg)), None),
             ("Sections", str(reg["Section"].nunique()), None),
             ("Approved / IFC", str(int(approved or 0)), None)])
    tabs = st.tabs(["Register", "Summary", "By month needed"])
    with tabs[0]:
        secs = list(dict.fromkeys(reg["Section"]))
        sel = st.multiselect("Sections", secs, default=secs, format_func=lambda s: s.split(" - ")[0])
        disc = sorted(reg["Discipline"].dropna().unique())
        dsel = st.multiselect("Discipline", disc, default=disc)
        f = reg[reg["Section"].isin(sel) & reg["Discipline"].isin(dsel)]
        cols = ["Drawing No.", "Drawing title", "Discipline", "Scale", "Sheet size", "Prepared by", "Checked / approved by",
                "Submitted to / purpose", "Needed by (programme month)", "Related BOQ item / activity", "Status", "Remarks"]
        table(f[[c for c in cols if c in f.columns]], height=620, raw=True)
        download_csv(reg, "drawing_register.csv")
    with tabs[1]:
        table(summ, pct_cols=("% approved",), label_col="Section")
        body = reg.groupby("Section").size().reset_index(name="Drawings")
        figure(charts.share_bar([s.split(" - ")[0] for s in body["Section"]], body["Drawings"] / body["Drawings"].sum(),
                                "Drawings by section (share)"))
    with tabs[2]:
        by = reg.groupby("Needed by (programme month)").size().reset_index(name="Drawings")
        by["n"] = by["Needed by (programme month)"].str.extract(r"M(\d+)").astype(int)
        by = by.sort_values("n")
        figure(charts.bar_compare(list(by["Needed by (programme month)"]), list(by["Drawings"]),
                                  "Number of drawings needed by programme month").update_traces(text=by["Drawings"]))
