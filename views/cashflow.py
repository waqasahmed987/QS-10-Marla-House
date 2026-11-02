"""Month-wise cost budget, S-curve and progress charts (sheet: Monthly Cash Flow)."""
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, metrics, mn, note, pct, table

TITLE = "Monthly Cash Flow & S-Curve"
ICON = "📈"


def render(S):
    d = extract.cashflow(S)
    st.title("Month-wise Cost Budget & S-Curve (route b)")
    note(d["note"])
    months = d["months"]
    short = [m.split(" ", 1)[-1] if " " in m else m for m in months]
    t = d["totals"]
    monthly = t["MONTHLY BUDGET (Rs)"]
    peak = max(monthly)
    metrics([
        ("Total budget", mn(d["grand_total"]), None),
        ("Peak month", mn(peak), short[monthly.index(peak)]),
        ("Duration", f"{len(months)} months", f"{short[0]} – {short[-1]}"),
        ("Reconciliation", "OK" if d["reconciliation"].startswith("OK") else "Check", None),
    ])
    tabs = st.tabs(["S-curve", "Progress by phase", "Gantt", "Budget lines", "Monthly totals"])
    with tabs[0]:
        figure(charts.s_curve(short, monthly, t["Cumulative % of total budget (S-curve)"],
                              t["Cumulative works progress % (physical S-curve)"]))
    with tabs[1]:
        ph = d["phases"]
        figure(charts.phase_stack(ph.rename(columns=dict(zip(months, short))), short))
        figure(charts.share_bar(ph["Phase"], ph["Share"], "Share of total budget by phase"))
        table(ph[["Phase", "Total (Rs)", "Share"]], pct_cols=("Share",))
    with tabs[2]:
        figure(charts.gantt(d["items"], short))
    with tabs[3]:
        items = d["items"]
        phases = list(dict.fromkeys(items["Phase"]))
        sel = st.multiselect("Filter phases", phases, default=phases)
        table(items[items["Phase"].isin(sel)], height=520, label_col="Activity")
        download_csv(items, "monthly_budget_lines.csv")
    with tabs[4]:
        import pandas as pd
        tot = pd.DataFrame({"Month": months, **{k: v for k, v in t.items()}})
        table(tot, pct_cols=[c for c in tot.columns if "%" in c], label_col="Month")
        download_csv(tot, "monthly_totals.csv")
