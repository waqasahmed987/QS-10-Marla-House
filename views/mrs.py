"""Searchable MRS Rawalpindi 2nd Bi-Annual 2026 schedule (sheet: MRS Schedule 2026)."""
import streamlit as st

from core import extract
from core.ui import download_csv, metrics, table

TITLE = "MRS 2026 Schedule"
ICON = "📚"


def render(S):
    st.title("MRS Rawalpindi – 2nd Bi-Annual 2026 Schedule of Rates")
    st.caption("Extracted from the Finance Department MRS (01.07.2026 – 31.12.2026), District Rawalpindi. "
               "Spot-check rates against the official PDF before tendering.")
    sch = extract.mrs_schedule(S)
    chapters = sch[["Ch.", "Chapter"]].drop_duplicates()
    labels = [f"{int(r['Ch.'])}. {r['Chapter']}" for _, r in chapters.iterrows()]
    metrics([("Rate lines", f"{len(sch):,}", None), ("Chapters", str(len(labels)), None)])
    c1, c2 = st.columns([2, 3])
    with c1:
        sel = st.multiselect("Chapters", labels, default=[])
    with c2:
        q = st.text_input("Search (e.g. 'brick work', 'Grade-60', 'emulsion', 'PPRC')")
    f = sch
    if sel:
        chs = [int(s.split(".")[0]) for s in sel]
        f = f[f["Ch."].isin(chs)]
    if q:
        blob = (f["Item description"].astype(str) + " " + f["Sub-head"].astype(str) + " " + f["Specification / size"].astype(str))
        for word in q.split():
            f = f[blob.str.contains(word, case=False, regex=False)]
            blob = blob[f.index]
    st.write(f"{len(f):,} matching lines")
    table(f.head(2000), height=600, label_col="Item description",
          decimals={c: 2 for c in f.columns if "rate" in c.lower()})
    if len(f) > 2000:
        st.caption("Showing first 2,000 lines - refine the search to see more.")
    download_csv(f, "mrs_2026_rawalpindi_filtered.csv", "Download filtered lines (CSV)")
