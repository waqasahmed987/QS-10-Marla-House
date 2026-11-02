"""Raw viewer for any sheet in the workbook - nothing is hidden."""
import pandas as pd
import streamlit as st

from core.ui import download_csv, table

TITLE = "All Sheets (raw)"
ICON = "🗂️"


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="all").dropna(axis=1, how="all")
    out = df.copy()
    out.insert(0, "Row", out.index)
    out.columns = ["Row"] + [chr(64 + c) if c <= 26 else f"C{c}" for c in df.columns]
    return out


def render(S):
    st.title("All Sheets – Raw View")
    st.caption("Every sheet of the workbook exactly as calculated in Excel (empty rows/columns removed). Column letters match Excel.")
    name = st.selectbox("Sheet", list(S.keys()), index=0)
    df = _clean(S[name])
    st.write(f"{len(df):,} rows × {len(df.columns) - 1} columns")
    table(df, height=650)
    download_csv(df, f"{name.replace(' ', '_')}.csv", "Download this sheet (CSV)")
