"""Overall Summary & Recommendation (sheet: Overall Summary)."""
import streamlit as st

from core import charts, extract
from core.ui import figure, metrics, mn, note, pct, table

TITLE = "Overall Summary"
ICON = "🏠"


def render(S):
    d = extract.overall(S)
    st.title("Overall Summary & Recommendation")
    note(d["subtitle"])
    costs = d["costs"]
    total = costs[costs["Cost head"].str.startswith("TOTAL")].iloc[0]
    rec = dict(d["recommendation"])
    metrics([
        ("Route (a) Owner materials + labour", mn(total["Route (a)"]), None),
        ("Route (b) Contractor at MRS rates", mn(total["Route (b)"]), None),
        ("Route (c) Architect/consultant design-build", mn(total["Route (c)"]), None),
    ])
    st.success(f"**Best overall value:** {rec.get('Best overall value (highest weighted score)', '-')}  \n"
               f"**Lowest cost:** {rec.get('Lowest-cost route', '-')}")

    t1, t2, t3, t4, t5 = st.tabs(["Costs", "Value evaluation", "Routes compared", "Risk matrix", "Recommendation"])
    with t1:
        main = costs.iloc[: costs.index[costs["Cost head"].str.startswith("TOTAL")][0]]
        figure(charts.stacked_costs(main.drop(columns=["Cheapest"]), "Cost head", ["Route (a)", "Route (b)", "Route (c)"],
                                    "Total cost to owner by cost head (Rs)"))
        table(costs, label_col="Cost head")
        st.subheader("If construction starts later (base escalation)")
        later = d["later"]
        figure(charts.lines(later, "Start year", ["Route (a)", "Route (b)", "Route (c)"], "Projected total cost by start year"))
        table(later)
    with t2:
        ev = d["evaluation"]
        table(ev, pct_cols=("Weight",), label_col="Criterion")
        ws = ev[ev["Criterion"].str.startswith("WEIGHTED")]
        if not ws.empty:
            row = ws.iloc[0]
            figure(charts.bar_compare(["Route (a)", "Route (b)", "Route (c)"],
                                      [row["Route (a)"], row["Route (b)"], row["Route (c)"]],
                                      "Weighted value score (higher = better)").update_traces(
                text=[f"{v:.2f}" for v in [row['Route (a)'], row['Route (b)'], row['Route (c)']]]))
    with t3:
        table(d["definitions"], raw=True)
    with t4:
        table(d["risk"], raw=True)
    with t5:
        for k, v in d["recommendation"]:
            if isinstance(v, (int, float)):
                v = mn(v) if abs(v) > 5 else pct(v)
            st.markdown(f"**{k}:** {v}")
