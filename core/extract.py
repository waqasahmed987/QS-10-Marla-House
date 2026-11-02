"""Sheet-specific extractors: turn each workbook sheet into tidy DataFrames / dicts.

Each function takes the dict returned by core.loader.load_sheets().
"""
from __future__ import annotations

import re

import pandas as pd

from .tables import CODE_RE, block, cell, find_row, headers, is_number, pairs, text

ROUTES = ["Route (b) Contractor at MRS rates", "Route (a) Owner materials + labour", "Option 1 Kohistan Arena (turnkey)"]


# ---------------------------------------------------------------- overall summary
def overall(S) -> dict:
    df = S["Overall Summary"]
    out = {"title": text(cell(df, 1, 1)), "subtitle": text(cell(df, 2, 1))}
    r = find_row(df, "Who designs")
    out["definitions"] = block(df, r - 1, 1, 4, stop_label="Workbook source",
                               names=["Aspect", "Route (a)", "Route (b)", "Route (c)"])
    ch = find_row(df, "Cost head")
    out["cost_header"] = headers(df, ch, 1, 5)
    out["costs"] = block(df, ch, 1, 5, stop_label="Expected construction duration",
                         names=["Cost head", "Route (a)", "Route (b)", "Route (c)", "Cheapest"])
    r = find_row(df, "Start year")
    out["later"] = block(df, r, 1, 4, names=["Start year", "Route (a)", "Route (b)", "Route (c)"])
    r = find_row(df, "Criterion")
    out["evaluation"] = block(df, r, 1, 6, stop_label="Value rank",
                              names=["Criterion", "Route (a)", "Route (b)", "Route (c)", "Weight", "Why"])
    r = find_row(df, "Risk / task")
    out["risk"] = block(df, r, 1, 4, names=["Risk / task", "Route (a)", "Route (b)", "Route (c)"])
    r = find_row(df, "Lowest-cost route")
    out["recommendation"] = pairs(df, r, 1, 2, stop_blank=False, max_rows=12)
    return out


# ---------------------------------------------------------------- 3-option summary
def summary(S) -> dict:
    df = S["Summary"]
    h = find_row(df, "Cost head")
    costs = block(df, h, 1, 4, stop_label="Of which solar", names=["Cost head", "Option A (MRS contract)",
                                                                  "Option B (self-managed)", "Option C (turnkey)"])
    e = find_row(df, "Criterion")
    ev = block(df, e, 1, 5, stop_label="Weighted score", names=["Criterion", "Option A", "Option B", "Option C", "Weight"])
    r = find_row(df, "QS RECOMMENDATION")
    rec = text(cell(df, r + 1, 1)) if r else ""
    best = pairs(df, find_row(df, "Lowest-cost option"), 1, 2)
    return {"costs": costs, "evaluation": ev, "recommendation": rec, "best": best}


# ---------------------------------------------------------------- contractor option 1
def contractor(S) -> dict:
    df = S["Contractor Option 1"]
    out = {"title": text(cell(df, 1, 1)), "subtitle": text(cell(df, 2, 1)), "note": text(cell(df, 3, 1))}
    r = find_row(df, "Contractor (Option No. 1)")
    out["particulars"] = pairs(df, r, 1, 2)
    q = find_row(df, "Quoted turnkey")
    out["quote"] = {"rate": cell(df, q, 2), "benchmark": cell(df, q, 4), "variance": cell(df, q, 5),
                    "price": cell(df, q + 1, 2), "design": cell(df, q + 2, 2), "solar": cell(df, q + 3, 2),
                    "pra": cell(df, q + 4, 2)}
    ch = find_row(df, "Cost head")
    out["cost_header"] = headers(df, ch, 1, 7)
    out["costs"] = block(df, ch, 1, 7, stop_label="10 kW solar share")
    w = find_row(df, "Work section")
    out["sections"] = block(df, w, 1, 7, stop_label="Total construction works")
    m = find_row(df, "Milestone (certified")
    out["milestones"] = block(df, m, 1, 7, stop_label="Total")
    y = find_row(df, "Start year")
    out["later"] = block(df, y, 1, 7, end_row=y + 2)
    p = find_row(df, "Party", exact=True)
    out["responsibilities"] = block(df, p, 1, 2, names=["Party", "Responsibilities"])
    c = find_row(df, "Check", exact=True)
    out["checks"] = block(df, c, 1, 3, stop_label="Checks verified", include_stop=False,
                          names=["Check", "Status", "Why it matters"])
    v = find_row(df, "Total cost to owner", start=find_row(df, "9. QS SUMMARY") or 1)
    out["verdict"] = pairs(df, v, 1, 2)
    return out


# ---------------------------------------------------------------- rent vs own
def rent(S) -> dict:
    df = S["Rent vs Own"]
    out = {"title": text(cell(df, 1, 1)), "note": text(cell(df, 2, 1))}
    i = find_row(df, "Input", exact=True)
    out["inputs"] = block(df, i, 1, 5, names=["Input", "_b", "_c", "Value", "Note"])[["Input", "Value", "Note"]]
    s = find_row(df, "Item", exact=True)
    out["summary"] = block(df, s, 1, 5, names=["Item", "_b", "_c", "Amount (Rs)", "Basis"])[["Item", "Amount (Rs)", "Basis"]]
    r = find_row(df, "Route", exact=True)
    out["routes"] = block(df, r, 1, 9, names=["Route", "_b", "_c", "Build months", "Move-in", "Rent until move-in",
                                              "Construction total", "Rent + construction", "vs route (b)"]).drop(columns=["_b", "_c"])
    c = find_row(df, "Checkpoint")
    out["checkpoints"] = block(df, c, 1, 9, names=["Checkpoint", "_b", "_c", "Date", "Keep renting: cumulative rent",
                                                   "Own: cumulative cash cost", "House value", "Own: net cost after house value",
                                                   "Advantage of owning"]).drop(columns=["_b", "_c"])
    out["breakeven"] = pairs(df, find_row(df, "Rent avoided in first year"), 1, 4)
    q = find_row(df, "D. QS SUMMARY")
    out["qs"] = [t for t, _ in pairs(df, q + 1, 1, 1)]
    m = find_row(df, "#", exact=True)
    monthly = block(df, m, 1, 17)
    monthly = monthly[monthly["Month"].notna()]
    out["monthly"] = monthly
    return out


# ---------------------------------------------------------------- monthly cash flow
def cashflow(S) -> dict:
    df = S["Monthly Cash Flow"]
    h = find_row(df, "Code", exact=True)
    months = [text(cell(df, h, c)).replace("\n", " ") for c in range(8, 24)]
    tot = find_row(df, "MONTHLY BUDGET (Rs)", col=2)
    rows = []
    section = ""
    for r in range(h + 2, tot):
        code, act = text(cell(df, r, 1)), cell(df, r, 2)
        if code and act is None and not is_number(cell(df, r, 4)):
            section = code
            continue
        if not code:
            continue
        rows.append([code, text(act), text(cell(df, r, 3)), cell(df, r, 4), cell(df, r, 5), cell(df, r, 6)]
                    + [cell(df, r, c) or 0 for c in range(8, 24)])
    items = pd.DataFrame(rows, columns=["Code", "Activity", "Phase", "Budget (Rs)", "Start", "End"] + months)
    totals = {}
    for k in range(6):
        label = text(cell(df, tot + k, 2))
        totals[label] = [cell(df, tot + k, c) for c in range(8, 24)]
    totals_total = cell(df, tot, 4)
    recon = text(cell(df, tot + 6, 4))
    p = find_row(df, "Phase", col=2, exact=True, start=tot)
    phase = []
    r = p + 1
    while text(cell(df, r, 2)) and text(cell(df, r, 2)) != "Total":
        phase.append([text(cell(df, r, 2)), cell(df, r, 4), cell(df, r, 5)] + [cell(df, r, c) or 0 for c in range(8, 24)])
        r += 1
    phases = pd.DataFrame(phase, columns=["Phase", "Total (Rs)", "Share"] + months)
    return {"months": months, "items": items, "totals": totals, "grand_total": totals_total,
            "reconciliation": recon, "phases": phases, "note": text(cell(df, 2, 1))}


# ---------------------------------------------------------------- drawing register
def drawings(S) -> dict:
    df = S["Drawing Register"]
    h = find_row(df, "Drawing No.")
    cols = headers(df, h, 1, 16)
    rows, section = [], ""
    for r in range(h + 1, df.index.max() + 1):
        a = text(cell(df, r, 1))
        if not a:
            continue
        if re.match(r"^[A-E]\. ", a) and cell(df, r, 2) is None:
            section = a
            continue
        if re.match(r"^[A-E]-[A-Z]{2}-\d{2}$", a):
            rows.append([section] + [cell(df, r, c) for c in range(1, 17)])
    reg = pd.DataFrame(rows, columns=["Section"] + cols)
    s = find_row(df, "Section", exact=True)
    summ = block(df, s, 1, 9, stop_label="TOTAL",
                 names=["Section", "_b", "Drawings", "Not started", "In preparation", "Submitted", "Approved / IFC",
                        "Revision req.", "% approved"]).drop(columns=["_b"])
    return {"register": reg, "summary": summ, "note": text(cell(df, 2, 1))}


# ---------------------------------------------------------------- responsibility matrix
def matrix(S) -> dict:
    df = S["Responsibility Matrix"]
    h = find_row(df, "No.", exact=True)
    last_col = max(c for c in df.columns if cell(df, h, c) is not None)
    cols = headers(df, h, 1, last_col)
    party_cols = cols[3:3 + (last_col - 7)]
    rows, phase = [], ""
    for r in range(h + 1, df.index.max() + 1):
        a, b = text(cell(df, r, 1)), cell(df, r, 2)
        if re.match(r"^\d\. ", a) and b is None:
            phase = a
            continue
        if re.match(r"^\d\.\d+$", a):
            rows.append([phase] + [cell(df, r, c) for c in range(1, last_col + 1)])
        elif a == "" and text(b).startswith("Number of activities"):
            break
    mat = pd.DataFrame(rows, columns=["Phase"] + cols)
    for pc in party_cols:
        mat[pc] = mat[pc].fillna("")
    pr = find_row(df, "Party", col=2, exact=True)
    roles = block(df, pr, 2, 3, names=["Party", "Role & responsibilities"])
    return {"matrix": mat, "parties": party_cols, "roles": roles, "note": text(cell(df, 2, 1))}


# ---------------------------------------------------------------- BOQ & MRS
def boq(S) -> dict:
    df = S["BOQ"]
    cols = headers(df, 4, 1, 14)
    rows, section = [], ""
    subtotals = []
    for r in range(5, df.index.max() + 1):
        a, b = text(cell(df, r, 1)), text(cell(df, r, 2))
        if len(a) == 1 and a in "ABCDE":
            section = f"{a}. {b.title()}"
        elif CODE_RE.match(a):
            rows.append([section] + [cell(df, r, c) for c in range(1, 15)])
        elif b.startswith("Sub-total"):
            subtotals.append([b, cell(df, r, 8), cell(df, r, 9), cell(df, r, 10), cell(df, r, 11), cell(df, r, 12)])
        elif b.startswith("GRAND TOTAL"):
            subtotals.append([b, cell(df, r, 8), cell(df, r, 9), cell(df, r, 10), cell(df, r, 11), cell(df, r, 12)])
    items = pd.DataFrame(rows, columns=["Section"] + cols)
    subs = pd.DataFrame(subtotals, columns=["Section", "MRS amount (A)", "Market amount (B)", "Turnkey amount (C)",
                                            "Difference MRS - Market", "% diff"])
    return {"items": items, "subtotals": subs}


def buildup(S) -> pd.DataFrame:
    df = S["MRS Rate Build-up"]
    return block(df, 4, 1, 11, end_row=df.index.max())


def mrs_schedule(S) -> pd.DataFrame:
    df = S["MRS Schedule 2026"]
    sch = block(df, 4, 1, 13, end_row=df.index.max())
    return sch[sch["Ref #"].notna()]


def materials(S) -> pd.DataFrame:
    df = S["Material Rates"]
    return block(df, 4, 1, 8)


def assumptions(S) -> pd.DataFrame:
    df = S["Assumptions"]
    return block(df, 3, 1, 3)


# ---------------------------------------------------------------- other costs & option D
def other_costs(S) -> pd.DataFrame:
    df = S["Other Costs"]
    cols = headers(df, 4, 1, 8)
    rows = []
    for r in range(5, df.index.max() + 1):
        a, b = text(cell(df, r, 1)), text(cell(df, r, 2))
        if a in ("PRE", "CON", "TAX", "UTL", "POST") and b:
            rows.append([cell(df, r, c) for c in range(1, 9)])
    return pd.DataFrame(rows, columns=cols)


def option_d(S) -> dict:
    df = S["Option D - Owner Supply"]
    h = find_row(df, "Code", exact=True, start=5)
    cols = headers(df, h, 1, 12)
    rows = []
    for r in range(h + 1, df.index.max() + 1):
        a = text(cell(df, r, 1))
        if CODE_RE.match(a):
            rows.append([cell(df, r, c) for c in range(1, 13)])
        if text(cell(df, r, 2)).startswith("TOTAL - MATERIALS"):
            break
    items = pd.DataFrame(rows, columns=cols)
    e = find_row(df, "Equipment", col=2, exact=True)
    equip = block(df, e, 1, 7, key_col=2, stop_label="TOTAL EQUIPMENT", )
    c = find_row(df, "Cost head", col=2, exact=True)
    comp = block(df, c, 2, 6, key_col=2, stop_label="Of which solar")
    return {"items": items, "equipment": equip, "comparison": comp}


# ---------------------------------------------------------------- solar
def solar(S) -> dict:
    df = S["Solar System"]
    summ = [(text(cell(df, r, 1)), cell(df, r, 4)) for r in range(5, 12)]
    p = find_row(df, "Parameter", exact=True)
    inputs = block(df, p, 1, 4)
    s = find_row(df, "Stage / item")
    build = block(df, s, 1, 6, stop_label="Installed cost per kWp")
    o = find_row(df, "Item", exact=True, start=s + 1)
    om = block(df, o, 1, 6, stop_label="TOTAL FIRST-YEAR")
    y = find_row(df, "Year", exact=True)
    sav = block(df, y, 1, 7, stop_label="Cumulative net saving")
    pb = pairs(df, find_row(df, "Simple payback"), 1, 2)
    return {"summary": summ, "inputs": inputs, "build": build, "om": om, "savings": sav, "payback": pb,
            "note": text(cell(df, 2, 1))}


# ---------------------------------------------------------------- forecast
def forecast(S) -> dict:
    df = S["5-Yr Forecast"]
    g = find_row(df, "Cost group", exact=True)
    esc = block(df, g, 1, 5)
    p = find_row(df, "Option / scenario")
    proj = block(df, p, 1, 7)
    proj = proj[proj["Option / scenario"].astype(str).str.startswith("Option")]
    w = find_row(df, "Item", exact=True)
    wait = block(df, w, 1, 7)
    u = find_row(df, "Material / rate")
    unit = block(df, u, 1, 8)
    return {"escalation": esc, "projection": proj, "waiting": wait, "unit_rates": unit}


# ---------------------------------------------------------------- analysis report
def report(S) -> list[tuple[str, str]]:
    """[(kind, text)] where kind is 'h' (heading) or 'p' (paragraph)."""
    df = S["Analysis Report"]
    out = [("t", text(cell(df, 1, 1))), ("s", text(cell(df, 2, 1)))]
    for r in range(4, df.index.max() + 1):
        t = text(cell(df, r, 1))
        if not t:
            continue
        out.append(("h" if re.match(r"^\d+\. [A-Z]", t) and len(t) < 70 else "p", t))
    return out
