"""10 Marla House – QS Cost Dashboard (Kohistan Enclave, Wah Cantt).

Run locally:   streamlit run app.py
Deploy:        push this folder to GitHub, then create an app on share.streamlit.io pointing to app.py
"""
import streamlit as st

from core.loader import DEFAULT_WORKBOOK, default_workbook_bytes, load_sheets, workbook_has_values
from core.theme import apply_theme, brand_block
from views import PAGES

st.set_page_config(page_title="QS Controls – 10 Marla House", page_icon="🛡️", layout="wide")
apply_theme()

# ---------------- sidebar: data source & navigation
with st.sidebar:
    brand_block()
    labels = [f"{p.ICON} {p.TITLE}" for p in PAGES]
    if st.session_state.get("nav") not in labels:
        st.session_state["nav"] = labels[0]
    choice = st.radio("Go to", labels, key="nav", label_visibility="collapsed")

    st.divider()
    uploaded = st.file_uploader("Use an updated workbook (.xlsx)", type=["xlsx"],
                                help="Edit the Excel file, SAVE it in Excel (so formulas are recalculated), then upload it here.")
    file_bytes = uploaded.getvalue() if uploaded is not None else default_workbook_bytes()
    source = uploaded.name if uploaded is not None else DEFAULT_WORKBOOK.name
    st.caption(f"Data source: **{source}**")
    st.download_button("⬇️ Download workbook", file_bytes, file_name=source,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------- load data
try:
    sheets = load_sheets(file_bytes)
except Exception as exc:  # unreadable / wrong file
    st.error(f"Could not read the workbook: {exc}")
    st.stop()

if not workbook_has_values(sheets):
    st.error("The workbook has no calculated values. Open it in Excel (or LibreOffice), press Save, then upload it again.")
    st.stop()

page = PAGES[labels.index(choice)]
try:
    page.render(sheets)
except Exception as exc:  # keep the app alive if a sheet layout was changed
    st.error(f"This page could not be built from the workbook ({type(exc).__name__}: {exc}). "
             "Check that the sheet layout was not changed, or view it under 'All Sheets (raw)'.")
    st.exception(exc)

st.sidebar.divider()
st.sidebar.caption("Figures are estimates for decision-making. Verify MRS rates, society charges and contractor quotations before signing.")
