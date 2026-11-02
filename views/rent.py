"""Rented house (since Nov-2022) + construction of own house (sheet: Rent vs Own)."""
import datetime as dt

import pandas as pd
import streamlit as st

from core import calc, charts, extract
from core.ui import download_csv, figure, metrics, mn, note, rs, table

TITLE = "Rent vs Own"
ICON = "🔑"


def render(S):
    d = extract.rent(S)
    st.title("Rented House + Construction of Own House")
    note(d["note"])
    summ = dict(zip(d["summary"]["Item"], d["summary"]["Amount (Rs)"]))
    metrics([
        ("Rent paid Nov-22 to Oct-26", mn(summ.get("Rent already paid (Nov-2022 to Oct-2026)")), None),
        ("Current monthly rent", rs(summ.get("Current monthly rent (Nov-2026 onward)")), None),
        ("Total rent until move-in", mn(summ.get("TOTAL RENT PAID UNTIL MOVE-IN")), None),
        ("Rent + new house", mn(summ.get("GRAND TOTAL: RENT (since 2022) + CONSTRUCTION OF NEW HOUSE")), None),
    ])
    be = dict(d["breakeven"])
    st.info(f"**Break-even (owning cheaper incl. house value):** "
            f"{be.get('Break-even: owning cheaper than renting (incl. house value)', '-')}  ·  "
            f"**On cash alone:** {be.get('Break-even on cash alone (ignoring house value)', '-')}")

    tabs = st.tabs(["Summary", "Charts", "Monthly schedule", "By building route", "What-if calculator", "Inputs"])
    m = d["monthly"].copy()
    with tabs[0]:
        table(d["summary"], label_col="Item")
        st.subheader("After completion: keep renting vs live in own house")
        table(d["checkpoints"], label_col="Checkpoint")
        for t in d["qs"]:
            st.markdown(f"- {t}")
    with tabs[1]:
        cols = ["Keep renting: cumulative rent (Rs)", "Own house: cumulative cost incl. construction (Rs)",
                "Own house: net cost after house value (Rs)"]
        figure(charts.lines(m, "Month", cols, "Cumulative cost: keep renting vs build & own",
                            colors=["#C00000", "#1F3864", "#70AD47"], dash={cols[2]: "dash"}))
        figure(charts.lines(m, "Month", ["Monthly rent (Rs) - market"], "Monthly rent (7% yearly increase)", colors=["#ED7D31"]))
        figure(charts.lines(m, "Month", ["Total outflow: rent + construction (Rs)"], "Monthly cash out: rent + construction",
                            colors=["#4472C4"]))
    with tabs[2]:
        phases = sorted(m["Phase"].dropna().unique())
        sel = st.multiselect("Show phases", phases, default=phases)
        years = sorted(int(y) for y in pd.to_datetime(m["Month"]).dt.year.unique())
        yr = st.select_slider("Years", options=years, value=(years[0], years[-1])) if len(years) > 1 else (years[0], years[0])
        f = m[m["Phase"].isin(sel) & pd.to_datetime(m["Month"]).dt.year.between(yr[0], yr[1])]
        table(f, height=520, label_col="Phase")
        download_csv(m, "rent_vs_own_monthly.csv")
    with tabs[3]:
        table(d["routes"], label_col="Route")
    with tabs[4]:
        st.caption("Recalculates the rent stream in the app (does not change the Excel file).")
        c1, c2, c3 = st.columns(3)
        with c1:
            rent0 = st.number_input("Initial rent (Rs/month)", min_value=0, value=27000, step=1000)
            start = st.date_input("Rent start", value=dt.date(2022, 11, 1))
        with c2:
            inc = st.slider("Yearly increase (%)", 0.0, 20.0, 7.0, 0.5) / 100
            move_in = st.date_input("Move-in month", value=dt.date(2028, 4, 1))
        with c3:
            horizon = st.date_input("Schedule end", value=dt.date(2040, 12, 1))
        sched = calc.rent_schedule(start, rent0, inc, horizon)
        until = calc.rent_until(sched, dt.date(move_in.year, move_in.month, 1))
        metrics([("Rent until move-in", rs(until), None),
                 ("Rent if never moving", rs(sched["Cumulative rent"].iloc[-1]), None),
                 ("Rent in final month", rs(sched["Monthly rent"].iloc[-1]), None)])
        figure(charts.lines(sched, "Month", ["Monthly rent"], "What-if monthly rent", colors=["#ED7D31"]))
    with tabs[5]:
        table(d["inputs"], label_col="Input", pct_rows_contain=("increase", "growth", "rate", "Escalation"))
