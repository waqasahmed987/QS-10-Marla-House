"""Load the QS workbook (values only) into one pandas DataFrame per sheet.

Every DataFrame is 1-indexed on both rows and columns so that row/column
numbers match what you see in Excel (row 5, column 2 = Excel B5).
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st
from openpyxl import load_workbook

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_WORKBOOK = DATA_DIR / "10_Marla_House_MRS_vs_Market_Wah_Cantt.xlsx"


def default_workbook_bytes() -> bytes:
    """Bytes of the workbook shipped with the app (data/ folder)."""
    return DEFAULT_WORKBOOK.read_bytes()


@st.cache_data(show_spinner="Reading workbook ...")
def load_sheets(file_bytes: bytes) -> dict[str, pd.DataFrame]:
    """Return {sheet name: DataFrame of cell values}.

    Uses the cached values Excel/LibreOffice saved with the file, so the
    workbook must have been saved by a spreadsheet program after editing
    (openpyxl cannot calculate formulas).
    """
    wb = load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
    sheets: dict[str, pd.DataFrame] = {}
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        df = pd.DataFrame(rows) if rows else pd.DataFrame()
        if not df.empty:
            df.index = range(1, len(df) + 1)
            df.columns = range(1, df.shape[1] + 1)
        sheets[ws.title] = df
    wb.close()
    return sheets


def workbook_has_values(sheets: dict[str, pd.DataFrame]) -> bool:
    """True if formulas have cached values (the key total is populated)."""
    df = sheets.get("Summary")
    if df is None or df.empty:
        return False
    for r in df.index:
        label = df.at[r, 1]
        if isinstance(label, str) and label.startswith("TOTAL COST"):
            return isinstance(df.at[r, 2], (int, float))
    return False
