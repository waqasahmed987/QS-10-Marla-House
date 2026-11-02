"""Generic helpers to locate tables inside a sheet DataFrame by their header text.

The workbook layout can shift by a few rows when inputs change, so every
extractor searches for header labels instead of using fixed row numbers.
"""
from __future__ import annotations

import re

import pandas as pd


def cell(df: pd.DataFrame, r: int | None, c: int):
    """Safe cell read (None if out of range)."""
    if r is None or df is None or df.empty:
        return None
    if r not in df.index or c not in df.columns:
        return None
    v = df.at[r, c]
    return None if (isinstance(v, float) and pd.isna(v)) else v


def text(v) -> str:
    return "" if v is None else str(v).strip()


def find_row(df: pd.DataFrame, label: str, col: int = 1, start: int = 1,
             exact: bool = False, end: int | None = None) -> int | None:
    """First row (>= start) whose cell in `col` starts with / equals `label`."""
    if df is None or df.empty or col not in df.columns:
        return None
    end = end or df.index.max()
    for r in range(start, end + 1):
        t = text(cell(df, r, col))
        if (t == label) if exact else t.startswith(label):
            return r
    return None


def headers(df: pd.DataFrame, row: int, c1: int, c2: int) -> list[str]:
    out, seen = [], {}
    for c in range(c1, c2 + 1):
        h = text(cell(df, row, c)).replace("\n", " ") or f"col{c}"
        if h in seen:
            seen[h] += 1
            h = f"{h} ({seen[h]})"
        else:
            seen[h] = 0
        out.append(h)
    return out


def block(df: pd.DataFrame, header_row: int | None, c1: int, c2: int, *,
          end_row: int | None = None, key_col: int | None = None,
          stop_label: str | None = None, include_stop: bool = True,
          names: list[str] | None = None) -> pd.DataFrame:
    """Read a rectangular table below `header_row`.

    Rows are read until: `end_row`, or the row whose key column starts with
    `stop_label` (included if include_stop), or the first blank key cell.
    """
    if header_row is None:
        return pd.DataFrame()
    cols = names or headers(df, header_row, c1, c2)
    key_col = key_col or c1
    data = []
    r = header_row + 1
    last = df.index.max()
    while r <= last:
        if end_row is not None and r > end_row:
            break
        key = text(cell(df, r, key_col))
        if stop_label and key.startswith(stop_label):
            if include_stop:
                data.append([cell(df, r, c) for c in range(c1, c2 + 1)])
            break
        if end_row is None and stop_label is None and key == "":
            break
        data.append([cell(df, r, c) for c in range(c1, c2 + 1)])
        r += 1
    return pd.DataFrame(data, columns=cols)


def pairs(df: pd.DataFrame, start: int, c_key: int = 1, c_val: int = 2,
          stop_blank: bool = True, max_rows: int = 50) -> list[tuple[str, object]]:
    """(label, value) rows starting at `start` until a blank label."""
    out = []
    for r in range(start, min(start + max_rows, df.index.max() + 1)):
        k = text(cell(df, r, c_key))
        if not k:
            if stop_blank:
                break
            continue
        out.append((k, cell(df, r, c_val)))
    return out


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not (isinstance(v, float) and pd.isna(v))


CODE_RE = re.compile(r"^[A-E]\d{1,2}$")
