"""Landing page in the 'project controls' style: hero text on the left, live project cards on the right."""
import streamlit as st

from core import extract, theme
from core.ui import mn

TITLE = "Home"
ICON = "✨"


def _go(label: str):
    st.session_state["nav"] = label


def _button(label, **kw):
    try:
        return st.button(label, width="stretch", **kw)
    except TypeError:  # older Streamlit
        return st.button(label, use_container_width=True, **kw)


def render(S):
    o = extract.overall(S)
    b = extract.boq(S)
    c = extract.contractor(S)
    sched = extract.mrs_schedule(S)
    dr = extract.drawings(S)
    mx = extract.matrix(S)

    costs = o["costs"]
    tot = costs[costs["Cost head"].str.startswith("TOTAL")].iloc[0]

    left, right = st.columns([1.15, 1], gap="large")
    with left:
        theme.pill("AI-Assisted Construction Cost Controls")
        theme.hero("Smart QS", "Cost Controls", "for Your Home",
                   "From MRS 2026 rates and BOQs to cash flow, contractor checks and rent-vs-own decisions — "
                   "<b>this dashboard prepares, compares, calculates and flags.</b> <em>You decide.</em>")
        st.write("")
        b1, b2, _ = st.columns([1.25, 1, 1.2])
        with b1:
            _button("Explore the Dashboard  →", type="primary", on_click=_go, args=("🏠 Overall Summary",))
        with b2:
            _button("Ask the AI", on_click=_go, args=("🤖 AI Assistant (Groq)",))
        theme.stats([
            (f"{len(sched):,}+", "MRS 2026 rates tracked"),
            (f"{len(dr['register'])}", "Drawings registered"),
            (f"{len(mx['matrix'])}", "Responsibility checks"),
            (mn(tot["Route (b)"]).replace("Rs ", "PKR "), "Recommended route total"),
        ])

    with right:
        # 1) payment-certificate style card from the contractor milestone schedule
        ms = c["milestones"]
        m3 = ms.iloc[2]
        gross = float(m3.iloc[2])
        ret = gross * 0.05
        theme.summary_card(
            "MILESTONE #3 — PAYMENT SUMMARY",
            [("Gross amount", mn(gross).replace("Rs ", "PKR "), ""),
             ("Retention (5%)", "– " + mn(ret).replace("Rs ", "PKR "), "neg"),
             ("Net payable", mn(gross - ret).replace("Rs ", "PKR "), "pos")],
            badge="Planned", foot=f"{m3.iloc[0]} · {m3.iloc[5]}")
        # 2) BOQ register card: sections at MRS rates, bar = share of works
        subs = b["subtotals"]
        body = subs[~subs["Section"].str.startswith("GRAND")]
        gt = subs[subs["Section"].str.startswith("GRAND")].iloc[0]["MRS amount (A)"]
        rows = []
        for _, r in body.iterrows():
            code = r["Section"].split(":")[0].replace("Sub-total ", "").strip()
            desc = r["Section"].split(":", 1)[-1].strip().title().split(" (")[0].replace("Mechanical, Electrical & Plumbing", "MEP Services")
            rows.append((f"GS-{code}", desc, mn(r["MRS amount (A)"]).replace("Rs ", "PKR "), r["MRS amount (A)"] / gt))
        theme.register_card("BOQ Register — 10 Marla Double Storey", rows, mn(gt).replace("Rs ", "PKR "), badge="MRS 2026")
        # 3) alert: item where MRS exceeds market the most
        it = b["items"]
        dcol = [x for x in it.columns if x.startswith("Difference")][0]
        pcol = [x for x in it.columns if x.startswith("% Diff")][0]
        top = it.loc[it[dcol].idxmax()]
        theme.alert_card(
            "Rate Overrun Detected",
            f"{top['Code']}: {str(top['Description'])[:60]} — MRS rate Rs {top.iloc[6]:,.0f} vs market Rs {top.iloc[7]:,.0f} "
            f"per {top.iloc[3]} ({top[pcol] * 100:+.0f}%). Human review required before certification.",
            f"QS RateCheck · BOQ {top['Code']}")
