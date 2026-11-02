"""Plotly chart builders used by the views."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

PALETTE = ["#F59E0B", "#3B82F6", "#10B981", "#A78BFA", "#F43F5E", "#FACC15", "#22D3EE", "#EA7A0C", "#94A3B8", "#6366F1"]
LAYOUT = dict(margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.2))

# dark, transparent template matching core/theme.py - applies to every Plotly figure in the app
pio.templates["qs"] = go.layout.Template(layout=dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=PALETTE,
    font=dict(family="Inter, sans-serif", color="#E6EAF2"), title=dict(font=dict(family="Archivo, sans-serif", size=18)),
    xaxis=dict(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.2)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.12)", zerolinecolor="rgba(148,163,184,0.2)")))
pio.templates.default = "plotly_dark+qs"


def bar_compare(labels, values, title, colors=None):
    labels, values = list(labels), list(values)
    colors = colors or [PALETTE[i % len(PALETTE)] for i in range(len(labels))]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=[f"Rs {v / 1e6:,.2f} M" for v in values], textposition="outside"))
    fig.update_layout(title=title, yaxis_title="Rs", **LAYOUT)
    fig.update_yaxes(tickformat=",")
    return fig


def stacked_costs(df: pd.DataFrame, label_col: str, value_cols: list[str], title: str):
    long = df.melt(id_vars=label_col, value_vars=value_cols, var_name="Option", value_name="Rs")
    fig = px.bar(long, x="Option", y="Rs", color=label_col, title=title, color_discrete_sequence=PALETTE)
    fig.update_layout(**LAYOUT)
    fig.update_yaxes(tickformat=",")
    return fig


def s_curve(months, monthly, cum_pct, works_pct):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=months, y=monthly, name="Monthly budget (Rs)", marker_color="#4472C4"), secondary_y=False)
    fig.add_trace(go.Scatter(x=months, y=cum_pct, name="Cumulative budget % (S-curve)", mode="lines+markers",
                             line=dict(color="#C00000", width=3)), secondary_y=True)
    fig.add_trace(go.Scatter(x=months, y=works_pct, name="Cumulative works progress %", mode="lines",
                             line=dict(color="#70AD47", width=2, dash="dash")), secondary_y=True)
    fig.update_layout(title="Monthly budget with S-curves", **LAYOUT)
    fig.update_yaxes(title_text="Rs per month", tickformat=",", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative %", tickformat=".0%", range=[0, 1.05], secondary_y=True)
    return fig


def phase_stack(phases: pd.DataFrame, months: list[str]):
    long = phases.melt(id_vars="Phase", value_vars=months, var_name="Month", value_name="Rs")
    fig = px.bar(long, x="Month", y="Rs", color="Phase", title="Progress summary - monthly budget by phase",
                 color_discrete_sequence=PALETTE, category_orders={"Month": months})
    fig.update_layout(**LAYOUT)
    fig.update_yaxes(tickformat=",")
    return fig


def share_bar(labels, shares, title):
    fig = go.Figure(go.Bar(y=labels, x=shares, orientation="h", marker_color="#ED7D31",
                           text=[f"{s * 100:.1f}%" for s in shares], textposition="outside"))
    fig.update_layout(title=title, **LAYOUT)
    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(autorange="reversed")
    return fig


def lines(df: pd.DataFrame, x: str, ys: list[str], title: str, y_title: str = "Rs", colors=None, dash=None):
    fig = go.Figure()
    for i, y in enumerate(ys):
        fig.add_trace(go.Scatter(x=df[x], y=df[y], name=y, mode="lines",
                                 line=dict(color=(colors or PALETTE)[i % len(PALETTE)],
                                           dash=(dash or {}).get(y, "solid"), width=2.5)))
    fig.update_layout(title=title, yaxis_title=y_title, **LAYOUT)
    fig.update_yaxes(tickformat=",")
    return fig


def gantt(items: pd.DataFrame, month_labels: list[str]):
    """Bar per activity from Start to End month (1-based programme months)."""
    df = items.copy()
    df["Start"] = pd.to_numeric(df["Start"], errors="coerce")
    df["End"] = pd.to_numeric(df["End"], errors="coerce")
    df = df.dropna(subset=["Start", "End"])
    df["Duration"] = df["End"] - df["Start"] + 1
    df["Label"] = df["Code"] + " " + df["Activity"].str.slice(0, 45)
    fig = px.bar(df, y="Label", x="Duration", base=df["Start"] - 0.5, color="Phase", orientation="h",
                 title="Programme bar chart (Gantt)", color_discrete_sequence=PALETTE,
                 hover_data={"Budget (Rs)": ":,.0f"})
    fig.update_yaxes(autorange="reversed", title=None)
    fig.update_xaxes(tickmode="array", tickvals=list(range(1, len(month_labels) + 1)), ticktext=month_labels,
                     title=None)
    fig.update_layout(height=max(500, 14 * len(df)), **LAYOUT)
    return fig


def pie(labels, values, title):
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.45, marker=dict(colors=PALETTE)))
    fig.update_layout(title=title, **LAYOUT)
    return fig
