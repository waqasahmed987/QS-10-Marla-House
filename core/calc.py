"""Small what-if calculators that run in Python (independent of Excel formulas)."""
from __future__ import annotations

import datetime as dt

import pandas as pd


def add_months(d: dt.date, n: int) -> dt.date:
    y, m = divmod(d.month - 1 + n, 12)
    return dt.date(d.year + y, m + 1, 1)


def rent_schedule(start: dt.date, rent0: float, increase: float, end: dt.date) -> pd.DataFrame:
    """Monthly rent with a fixed yearly increase on each anniversary of `start`."""
    rows, d, i = [], dt.date(start.year, start.month, 1), 0
    while d <= end:
        rows.append({"Month": d, "Rent year": i // 12 + 1, "Monthly rent": rent0 * (1 + increase) ** (i // 12)})
        d, i = add_months(d, 1), i + 1
    df = pd.DataFrame(rows)
    df["Cumulative rent"] = df["Monthly rent"].cumsum()
    return df


def rent_until(schedule: pd.DataFrame, move_in: dt.date) -> float:
    return float(schedule.loc[schedule["Month"] < move_in, "Monthly rent"].sum())


def escalate(amount: float, rate: float, years: float) -> float:
    return amount * (1 + rate) ** years
