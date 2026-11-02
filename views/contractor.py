"""Contractor Hired Option No. 1 - Kohistan Arena Real Estate & Builders."""
import streamlit as st

from core import charts, extract
from core.ui import download_csv, figure, metrics, mn, note, pct, rs, table

TITLE = "Contractor Option 1"
ICON = "🏗️"


def render(S):
    d = extract.contractor(S)
    st.title(d["title"].title().replace("No. 1 -", "No. 1 –"))
    st.markdown(f"**{d['subtitle']}**")
    st.warning(d["note"])
    q = d["quote"]
    costs = d["costs"]
    head = d["cost_header"]
    tot = costs[costs[head[0]].astype(str).str.startswith("TOTAL")].iloc[0]
    metrics([
        ("Quoted / estimated rate", f"Rs {q['rate']:,.0f}/sft", f"{q['variance'] * 100:+.1f}% vs QS benchmark"),
        ("Construction contract", mn(q["price"]), None),
        ("Total cost to owner", mn(tot[head[1]]), f"{(tot[head[1]] / tot[head[3]] - 1) * 100:+.1f}% vs route (b)"),
        ("Route (b) benchmark", mn(tot[head[3]]), None),
    ])
    st.caption(f"Design included: **{q['design']}** · Solar included: **{q['solar']}** · PRA-registered: **{q['pra']}**. "
               "Change these in the Excel file (sheet 'Contractor Option 1', yellow cells) and re-upload it in the sidebar.")

    tabs = st.tabs(["Cost to owner", "Work sections", "Payment milestones", "Responsibilities", "Due-diligence checklist", "Verdict"])
    with tabs[0]:
        figure(charts.bar_compare(head[1:5], [tot[h] for h in head[1:5]], "Total cost to owner (Rs)"))
        table(costs, label_col=head[0])
        st.subheader("If the contract is signed later")
        table(d["later"], label_col=d["later"].columns[0])
    with tabs[1]:
        sec = d["sections"]
        c0 = sec.columns[0]
        body = sec[~sec[c0].astype(str).str.startswith("Total")]
        figure(charts.pie(body[c0], body[sec.columns[1]], "Construction price by work section"))
        table(sec, pct_cols=(sec.columns[5],), label_col=c0)
    with tabs[2]:
        ms = d["milestones"]
        table(ms, pct_cols=(ms.columns[1], ms.columns[4]), label_col=ms.columns[0])
        download_csv(ms, "payment_milestones.csv")
    with tabs[3]:
        table(d["responsibilities"], raw=True)
    with tabs[4]:
        ck = d["checks"]
        done = (ck["Status"] == "Verified").sum()
        st.progress(done / len(ck) if len(ck) else 0, text=f"{done} of {len(ck)} checks verified")
        table(ck, raw=True)
    with tabs[5]:
        for k, v in d["verdict"]:
            if k == "Recommendation":
                st.error(f"**{k}:** {v}") if "NEGOTIATION" in str(v) else st.success(f"**{k}:** {v}")
            else:
                st.markdown(f"**{k}:** {v}")
        st.markdown("**Contract particulars**")
        for k, v in d["particulars"]:
            st.markdown(f"- **{k}:** {v}")
