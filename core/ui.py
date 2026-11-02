"""Display helpers: number formatting, tables, metric cards and figures."""
from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st


def rs(v, decimals: int = 0) -> str:
    """Format a number as Pakistani rupees, e.g. Rs 27,706,151."""
    if v is None or (isinstance(v, float) and pd.isna(v)) or not isinstance(v, (int, float)):
        return "-" if v is None else str(v)
    return f"Rs {v:,.{decimals}f}"


def mn(v) -> str:
    """Format as rupees in millions, e.g. Rs 27.71 M."""
    if not isinstance(v, (int, float)) or pd.isna(v):
        return "-"
    return f"Rs {v / 1e6:,.2f} M"


def pct(v, decimals: int = 1) -> str:
    if not isinstance(v, (int, float)) or pd.isna(v):
        return "-"
    return f"{v * 100:.{decimals}f}%"


def num(v, decimals: int = 0) -> str:
    if not isinstance(v, (int, float)) or pd.isna(v):
        return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)
    return f"{v:,.{decimals}f}"


def fmt_table(df: pd.DataFrame, pct_cols=(), pct_rows_contain=("%", "share", "Share"),
              label_col: str | None = None, decimals: dict | None = None) -> pd.DataFrame:
    """Return a display copy with numbers formatted as text.

    - columns listed in pct_cols are shown as percentages
    - rows whose label (label_col) contains any pct_rows_contain token are shown as %
    - dates are shown as Mon-YYYY
    """
    decimals = decimals or {}
    out = df.astype(object).copy()
    label_col = label_col or (out.columns[0] if len(out.columns) else None)
    for i in out.index:
        label = str(out.at[i, label_col]) if label_col in out.columns else ""
        row_is_pct = any(tok in label for tok in pct_rows_contain) and "Rs" not in label
        for c in out.columns:
            v = out.at[i, c]
            if isinstance(v, (dt.datetime, dt.date)):
                out.at[i, c] = v.strftime("%b-%Y")
            elif isinstance(v, (int, float)) and not (isinstance(v, float) and pd.isna(v)) and not isinstance(v, bool):
                if c in pct_cols or (row_is_pct and c != label_col and abs(v) <= 5):
                    out.at[i, c] = pct(v)
                else:
                    out.at[i, c] = num(v, decimals.get(c, 0 if abs(v) >= 100 or float(v).is_integer() else 2))
            elif v is None or (isinstance(v, float) and pd.isna(v)):
                out.at[i, c] = ""
    return out.astype(str)


def table(df: pd.DataFrame, height: int | None = None, **fmt_kwargs) -> None:
    """Show a formatted, full-width table."""
    raw = fmt_kwargs.pop("raw", False)
    shown = df if raw else fmt_table(df, **fmt_kwargs)
    kwargs = {"hide_index": True}
    if height:
        kwargs["height"] = height
    try:
        st.dataframe(shown, width="stretch", **kwargs)
    except TypeError:  # older Streamlit
        st.dataframe(shown, use_container_width=True, **kwargs)


def figure(fig) -> None:
    """Show a Plotly figure full width (works on old and new Streamlit)."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def metrics(items: list[tuple[str, str, str | None]], cols: int | None = None) -> None:
    """Row of metric cards: [(label, value, delta_or_None)]."""
    cs = st.columns(cols or len(items))
    for c, (label, value, delta) in zip(cs, items):
        with c:
            st.metric(label, value, delta)


def download_csv(df: pd.DataFrame, filename: str, label: str = "Download table (CSV)") -> None:
    st.download_button(label, df.to_csv(index=False).encode("utf-8"), file_name=filename, mime="text/csv")


def note(text_: str) -> None:
    if text_:
        st.caption(text_)
