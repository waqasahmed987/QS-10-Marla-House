"""Dark 'project-controls' theme: global CSS + small HTML components (hero, pills, glass cards, alerts).

Call apply_theme() once at the top of app.py. All components return/emit plain HTML via st.markdown.
Change BRAND / colours here to restyle the whole app.
"""
from __future__ import annotations

import html

import streamlit as st

BRAND = "QS Controls"
BRAND_SUB = "10 Marla House · Kohistan Enclave"
VERSION = "v1.0"

C = {  # palette
    "bg": "#0A0F1E", "bg2": "#0E1528", "card": "rgba(17, 25, 45, 0.72)", "line": "rgba(148, 163, 184, 0.14)",
    "text": "#E6EAF2", "muted": "#94A3B8", "orange": "#F59E0B", "orange2": "#EA7A0C", "blue": "#3B82F6",
    "green": "#10B981", "red": "#F43F5E", "purple": "#A78BFA", "yellow": "#FACC15",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@600;800;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

/* ---------- page background: navy + faint grid + glow ---------- */
.stApp {{
  background:
    radial-gradient(1200px 600px at 75% 20%, rgba(59,130,246,0.10), transparent 60%),
    radial-gradient(900px 500px at 10% 90%, rgba(245,158,11,0.06), transparent 60%),
    linear-gradient({C['line']} 1px, transparent 1px) 0 0 / 64px 64px,
    linear-gradient(90deg, {C['line']} 1px, transparent 1px) 0 0 / 64px 64px,
    {C['bg']};
  color: {C['text']};
}}
html, body, [class*="css"], .stMarkdown, p, li, label {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3, .qs-display {{ font-family: 'Archivo','Inter',system-ui,-apple-system,'Segoe UI',sans-serif !important; letter-spacing: -0.02em; }}
h1 {{ font-weight: 900 !important; }}
h2, h3 {{ font-weight: 800 !important; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 1400px; }}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, {C['bg2']} 0%, {C['bg']} 100%);
  border-right: 1px solid {C['line']};
}}
section[data-testid="stSidebar"] label p {{ font-size: 0.95rem; }}

/* ---------- buttons ---------- */
.stButton > button, .stDownloadButton > button {{
  border-radius: 12px; border: 1px solid {C['line']}; background: rgba(30,41,64,0.7); color: {C['text']};
  font-weight: 600; padding: 0.55rem 1.1rem; transition: all .15s ease;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{ border-color: {C['orange']}; color: #fff; }}
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, {C['orange']} 0%, {C['orange2']} 100%); color: #111 !important; border: 0;
  box-shadow: 0 10px 30px -8px rgba(245,158,11,0.55);
}}

/* ---------- metric cards ---------- */
div[data-testid="stMetric"] {{
  background: {C['card']}; border: 1px solid {C['line']}; border-radius: 16px; padding: 14px 18px;
  backdrop-filter: blur(8px); box-shadow: 0 20px 40px -24px rgba(0,0,0,0.6);
}}
div[data-testid="stMetricLabel"] p {{ color: {C['muted']} !important; font-size: 0.82rem; }}
div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace; font-weight: 600; }}

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {C['line']}; }}
.stTabs [data-baseweb="tab"] {{
  background: rgba(30,41,64,0.45); border-radius: 10px 10px 0 0; padding: 8px 16px; color: {C['muted']};
}}
.stTabs [aria-selected="true"] {{ color: #fff !important; background: rgba(245,158,11,0.14) !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {C['orange']}; }}

/* ---------- tables, inputs, alerts ---------- */
div[data-testid="stDataFrame"] {{ border: 1px solid {C['line']}; border-radius: 14px; overflow: hidden; }}
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{ background: rgba(17,25,45,0.8); border-color: {C['line']}; }}
div[data-testid="stAlert"] {{ border-radius: 14px; border: 1px solid {C['line']}; }}
div[data-testid="stPlotlyChart"] {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 16px; padding: 6px; }}
hr {{ border-color: {C['line']}; }}

/* ---------- custom components ---------- */
.qs-brand {{ display:flex; align-items:center; gap:12px; margin-bottom: 6px; }}
.qs-logo {{ width:44px; height:44px; border-radius:12px; display:grid; place-items:center;
  background: linear-gradient(135deg, #4F46E5, #2563EB); box-shadow: 0 0 0 1px rgba(255,255,255,0.08), 0 10px 25px -10px #4F46E5; }}
.qs-brand-name {{ font-family:'Archivo','Inter',system-ui,-apple-system,'Segoe UI',sans-serif; font-weight:800; font-size:1.25rem; color:#9DB7FF; }}
.qs-ver {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; font-size:0.7rem; color:{C['yellow']}; border:1px solid rgba(250,204,21,0.45);
  border-radius:6px; padding:1px 6px; margin-left:6px; }}
.qs-brand-sub {{ color:{C['muted']}; font-size:0.82rem; }}

.qs-pill {{ display:inline-flex; align-items:center; gap:8px; padding:7px 16px; border-radius:999px;
  border:1px solid rgba(59,130,246,0.35); background: rgba(30,58,138,0.25); color:#BFD3FF; font-size:0.92rem; }}
.qs-pill::before {{ content:''; width:7px; height:7px; border-radius:50%; background:{C['blue']}; box-shadow:0 0 10px {C['blue']}; }}

.qs-hero {{ font-family:'Archivo','Inter',system-ui,-apple-system,'Segoe UI',sans-serif; font-weight:900; line-height:0.98; letter-spacing:-0.035em;
  font-size: clamp(2.6rem, 5.6vw, 5.4rem); color:#fff; margin: 18px 0 18px 0; }}
.qs-grad {{ background: linear-gradient(90deg, {C['yellow']} 0%, {C['orange']} 45%, {C['orange2']} 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent; }}
.qs-lead {{ font-size: 1.22rem; color:{C['muted']}; line-height:1.6; max-width: 820px; }}
.qs-lead b {{ color:{C['text']}; font-weight:500; }}
.qs-lead em {{ color:{C['yellow']}; font-style:normal; }}

.qs-stats {{ display:flex; gap:42px; flex-wrap:wrap; margin-top: 26px; }}
.qs-stat-v {{ font-family:'Archivo','Inter',system-ui,-apple-system,'Segoe UI',sans-serif; font-weight:800; font-size:1.65rem; color:#fff; }}
.qs-stat-l {{ color:{C['muted']}; font-size:0.85rem; }}

.qs-card {{ background:{C['card']}; border:1px solid {C['line']}; border-radius:18px; padding:18px 22px;
  backdrop-filter: blur(10px); box-shadow: 0 30px 60px -30px rgba(0,0,0,0.75); margin-bottom: 16px; }}
.qs-card-h {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }}
.qs-card-t {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; font-weight:600; color:#fff; font-size:0.95rem; }}
.qs-card-t::before {{ content:'●'; color:{C['green']}; margin-right:8px; }}
.qs-badge {{ font-size:0.78rem; padding:3px 10px; border-radius:999px; border:1px solid rgba(16,185,129,0.45);
  color:{C['green']}; background:rgba(16,185,129,0.08); }}
.qs-badge.warn {{ border-color: rgba(245,158,11,0.5); color:{C['orange']}; background:rgba(245,158,11,0.08); }}

.qs-row {{ display:grid; grid-template-columns: 64px 1fr 170px; gap:12px; align-items:center;
  padding:11px 0; border-top:1px solid {C['line']}; }}
.qs-code {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; color:{C['blue']}; font-size:0.82rem; }}
.qs-desc {{ color:{C['text']}; }}
.qs-amt {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; font-size:0.82rem; color:{C['muted']}; text-align:right; }}
.qs-bar {{ height:4px; border-radius:4px; background: rgba(148,163,184,0.18); margin-top:6px; overflow:hidden; }}
.qs-bar > span {{ display:block; height:100%; border-radius:4px; }}
.qs-total {{ text-align:right; font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; font-weight:600; color:#fff; padding-top:12px;
  border-top:1px solid {C['line']}; }}

.qs-kv {{ display:flex; justify-content:space-between; padding:7px 0; color:{C['muted']}; }}
.qs-kv span:last-child {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; font-weight:600; color:#fff; }}
.qs-kv.neg span:last-child {{ color:{C['red']}; }}
.qs-kv.pos span:last-child {{ color:{C['green']}; }}
.qs-foot {{ color:{C['muted']}; font-size:0.8rem; margin-top:10px; padding-top:10px; border-top:1px solid {C['line']}; }}
.qs-foot::before {{ content:'●'; color:{C['green']}; margin-right:8px; }}

.qs-alert {{ background: linear-gradient(180deg, rgba(41,26,6,0.92), rgba(20,14,6,0.92)); border:1px solid rgba(245,158,11,0.45);
  border-radius:18px; padding:18px 22px; display:flex; gap:16px; box-shadow: 0 30px 60px -30px rgba(245,158,11,0.35); }}
.qs-alert-icon {{ width:40px; height:40px; flex:0 0 40px; border-radius:10px; display:grid; place-items:center;
  background: rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.35); }}
.qs-alert-t {{ font-weight:600; color:{C['orange']}; font-size:1.02rem; }}
.qs-alert-b {{ color:#CBD5E1; margin:6px 0 8px 0; line-height:1.5; }}
.qs-alert-m {{ font-family:'JetBrains Mono',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace; color:{C['purple']}; font-size:0.8rem; }}

.qs-section {{ font-family:'Archivo','Inter',system-ui,-apple-system,'Segoe UI',sans-serif; font-weight:800; font-size:1.6rem; color:#fff; margin: 8px 0 4px 0; }}
.qs-muted {{ color:{C['muted']}; }}
</style>
"""

SHIELD = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
          '<path d="m9 12 2 2 4-4"/></svg>')


def _md(h: str) -> None:
    st.markdown(h, unsafe_allow_html=True)


def apply_theme() -> None:
    _md(CSS)


def esc(t) -> str:
    return html.escape(str(t))


def brand_block() -> None:
    _md(f"""<div class="qs-brand"><div class="qs-logo">{SHIELD.format(c='#fff')}</div>
    <div><div class="qs-brand-name">{esc(BRAND)}<span class="qs-ver">{VERSION}</span></div>
    <div class="qs-brand-sub">{esc(BRAND_SUB)}</div></div></div>""")


def pill(text_: str) -> None:
    _md(f'<span class="qs-pill">{esc(text_)}</span>')


def hero(line1: str, line2_grad: str, line3: str, lead_html: str) -> None:
    _md(f"""<div class="qs-hero">{esc(line1)}<br><span class="qs-grad">{esc(line2_grad)}</span><br>{esc(line3)}</div>
    <div class="qs-lead">{lead_html}</div>""")


def stats(items: list[tuple[str, str]]) -> None:
    cells = "".join(f'<div><div class="qs-stat-v">{esc(v)}</div><div class="qs-stat-l">{esc(l)}</div></div>' for v, l in items)
    _md(f'<div class="qs-stats">{cells}</div>')


def register_card(title: str, rows: list[tuple[str, str, str, float]], total: str, badge: str | None = None) -> None:
    """rows = [(code, description, amount_text, progress 0..1)]"""
    colours = [C["orange"], C["yellow"], C["green"], C["blue"], C["purple"]]
    body = ""
    for i, (code, desc, amt, p) in enumerate(rows):
        p = max(0.0, min(1.0, float(p)))
        body += (f'<div class="qs-row"><div class="qs-code">{esc(code)}</div><div class="qs-desc">{esc(desc)}</div>'
                 f'<div><div class="qs-amt">{esc(amt)} · {p * 100:.0f}%</div>'
                 f'<div class="qs-bar"><span style="width:{p * 100:.0f}%;background:{colours[i % len(colours)]}"></span></div></div></div>')
    b = f'<span class="qs-badge">{esc(badge)}</span>' if badge else ""
    _md(f'<div class="qs-card"><div class="qs-card-h"><div class="qs-card-t">{esc(title)}</div>{b}</div>{body}'
        f'<div class="qs-total">Total: {esc(total)}</div></div>')


def summary_card(title: str, rows: list[tuple[str, str, str]], badge: str = "Certified", foot: str = "") -> None:
    """rows = [(label, value, kind)] with kind in '', 'neg', 'pos'"""
    body = "".join(f'<div class="qs-kv {k}"><span>{esc(l)}</span><span>{esc(v)}</span></div>' for l, v, k in rows)
    f = f'<div class="qs-foot">{esc(foot)}</div>' if foot else ""
    _md(f'<div class="qs-card"><div class="qs-card-h"><div class="qs-card-t" style="font-family:Inter,system-ui,sans-serif">{esc(title)}</div>'
        f'<span class="qs-badge">{esc(badge)}</span></div>{body}{f}</div>')


def alert_card(title: str, body: str, meta: str, level: str = "high") -> None:
    _md(f"""<div class="qs-alert"><div class="qs-alert-icon">{SHIELD.format(c=C['orange'])}</div><div>
    <div class="qs-alert-t">{esc(title)} <span class="qs-badge warn">{esc(level)}</span></div>
    <div class="qs-alert-b">{esc(body)}</div><div class="qs-alert-m">{esc(meta)}</div></div></div>""")


def section(title: str, sub: str = "") -> None:
    _md(f'<div class="qs-section">{esc(title)}</div>' + (f'<div class="qs-muted">{esc(sub)}</div>' if sub else ""))
