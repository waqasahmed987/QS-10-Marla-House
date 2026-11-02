"""QS analysis report (sheet: Analysis Report)."""
import streamlit as st

from core import extract

TITLE = "QS Analysis Report"
ICON = "📝"


def render(S):
    parts = extract.report(S)
    md = []
    for kind, t in parts:
        if kind == "t":
            st.title(t)
            md.append(f"# {t}\n")
        elif kind == "s":
            st.caption(t)
            md.append(f"_{t}_\n")
        elif kind == "h":
            st.subheader(t)
            md.append(f"\n## {t}\n")
        else:
            st.markdown(t)
            md.append(f"{t}\n")
    st.download_button("Download report (Markdown)", "\n".join(md).encode("utf-8"),
                       file_name="QS_analysis_report.md", mime="text/markdown")
