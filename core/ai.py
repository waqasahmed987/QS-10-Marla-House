"""Groq AI helper: reads the API key and builds a compact text context from the workbook."""
from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from . import extract

# Self-serve Groq models (Llama models became Enterprise-only on 26-Aug-2026).
MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]


def get_api_key() -> str | None:
    """Key order: Streamlit secrets -> environment variable -> key typed in the sidebar (session only)."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:  # no secrets.toml present
        key = None
    return key or os.environ.get("GROQ_API_KEY") or st.session_state.get("groq_key_typed")


def _csv(df: pd.DataFrame, max_rows: int = 60) -> str:
    df = df.head(max_rows).astype(object).copy()
    for c in df.columns:
        df[c] = df[c].map(lambda v: (int(round(v)) if abs(v) >= 100 else round(v, 3)) if isinstance(v, float) else v)
    return df.to_csv(index=False)


@st.cache_data(show_spinner=False)
def build_context(_sheets: dict, cache_key: str) -> str:
    """Key figures from every sheet as plain text for the model (kept short to save tokens)."""
    S = _sheets
    parts = ["PROJECT: 10 Marla double-storey house (3,400 sft covered), Kohistan Enclave, Wah Cantt, Pakistan. "
             "Prices PKR, Nov 2026. Rates from MRS Rawalpindi 2nd Bi-Annual 2026 and Wah market."]
    try:
        o = extract.overall(S)
        parts += ["## OVERALL SUMMARY - routes: (a) owner materials + labour contract, (b) contractor at MRS item rates, "
                  "(c) architect/consultant design-build", _csv(o["costs"]), _csv(o["evaluation"]),
                  "Recommendation: " + "; ".join(f"{k}: {v}" for k, v in o["recommendation"]),
                  "Start-later totals:\n" + _csv(o["later"])]
    except Exception as e:
        parts.append(f"(overall summary unavailable: {e})")
    try:
        c = extract.contractor(S)
        parts += ["## CONTRACTOR OPTION 1 - KOHISTAN ARENA REAL ESTATE & BUILDERS (turnkey)",
                  f"Quote inputs: {c['quote']}", _csv(c["costs"]), _csv(c["milestones"]),
                  "Verdict: " + " | ".join(f"{k}: {v}" for k, v in c["verdict"])]
    except Exception as e:
        parts.append(f"(contractor unavailable: {e})")
    try:
        r = extract.rent(S)
        parts += ["## RENT VS OWN (rent since Nov-2022 Rs 27,000, +7%/yr)", _csv(r["summary"]), _csv(r["routes"]),
                  _csv(r["checkpoints"]), " ".join(r["qs"][:5])]
    except Exception as e:
        parts.append(f"(rent unavailable: {e})")
    try:
        cf = extract.cashflow(S)
        tot = pd.DataFrame({"Month": cf["months"], **cf["totals"]})
        parts += ["## MONTHLY CASH FLOW (route b)", _csv(tot), _csv(cf["phases"][["Phase", "Total (Rs)", "Share"]])]
    except Exception as e:
        parts.append(f"(cash flow unavailable: {e})")
    try:
        b = extract.boq(S)
        it = b["items"]
        diff = [c for c in it.columns if c.startswith("Difference")][0]
        top = it.reindex(it[diff].abs().sort_values(ascending=False).index).head(12)
        parts += ["## BOQ SUBTOTALS (A=MRS item rates, B=market, C=turnkey)", _csv(b["subtotals"]),
                  "12 BOQ items with the largest MRS-vs-market difference (code, description, unit, qty, MRS rate, market rate, difference):\n" +
                  _csv(top.iloc[:, [1, 2, 3, 5, 6, 7, 11]])]
    except Exception as e:
        parts.append(f"(BOQ unavailable: {e})")
    try:
        od = extract.option_d(S)
        eq = od["equipment"]
        parts += ["## OPTIONS A-D COMPARISON", _csv(od["comparison"]),
                  "Equipment hire (route a):\n" + _csv(eq.iloc[:, [1, 2, 3, 4, 5]])]
    except Exception as e:
        parts.append(f"(option D unavailable: {e})")
    try:
        so = extract.solar(S)
        parts += ["## SOLAR 10 kW", "; ".join(f"{k}: {v}" for k, v in so["summary"]),
                  "Payback: " + "; ".join(f"{k}: {v}" for k, v in so["payback"] if v is not None)]
    except Exception as e:
        parts.append(f"(solar unavailable: {e})")
    try:
        f = extract.forecast(S)
        proj = f["projection"]
        parts += ["## 5-YEAR FORECAST (base scenario)", _csv(proj[proj.iloc[:, 0].astype(str).str.endswith("Base")]),
                  _csv(f["escalation"].iloc[:, :4])]
    except Exception as e:
        parts.append(f"(forecast unavailable: {e})")
    try:
        parts += ["## ASSUMPTIONS", _csv(extract.assumptions(S).iloc[:, :2], 45),
                  "## MATERIAL RATES (MRS indicative vs Wah market)", _csv(extract.materials(S).iloc[:, :6])]
    except Exception as e:
        parts.append(f"(assumptions unavailable: {e})")
    try:
        d = extract.drawings(S)
        parts += ["## DRAWING REGISTER SUMMARY", _csv(d["summary"])]
        m = extract.matrix(S)
        lead = [c for c in m["matrix"].columns if c.startswith("Lead")][0]
        counts = m["matrix"].groupby(lead).size().sort_values(ascending=False)
        parts += ["## RESPONSIBILITY MATRIX - activities led per party (55 activities, route b)",
                  "; ".join(f"{k}: {v}" for k, v in counts.items())]
    except Exception as e:
        parts.append(f"(drawings/matrix unavailable: {e})")
    return "\n\n".join(parts)


SYSTEM_PROMPT = (
    "You are a quantity surveyor's assistant for a house construction project in Pakistan. "
    "Answer ONLY from the project data below. Quote rupee figures exactly as given (Rs with thousands separators) "
    "and name the sheet they come from. If the data does not contain the answer, say so and suggest which sheet "
    "or input to check. Be concise; use short tables or bullet points. Do not invent rates, laws or company facts.\n\n"
    "PROJECT DATA:\n"
)
