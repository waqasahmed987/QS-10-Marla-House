"""AI assistant (Groq) that answers questions about the workbook."""
import hashlib

import streamlit as st

from core import ai

TITLE = "AI Assistant (Groq)"
ICON = "🤖"

EXAMPLES = [
    "Which route should I choose and why?",
    "How much more does Kohistan Arena cost than the MRS item-rate contract?",
    "What is my peak monthly payment and when?",
    "How much rent will I have paid until I move in?",
    "Which BOQ items are most expensive under MRS compared with market rates?",
]


def _stream(client, model, messages):
    stream = client.chat.completions.create(model=model, messages=messages, temperature=0.2,
                                            max_completion_tokens=1500, stream=True)
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece


def render(S):
    st.title("🤖 Ask the QS Assistant")
    st.caption("Answers come from the workbook figures, using Groq's hosted models. Verify important numbers on the sheets.")

    key = ai.get_api_key()
    with st.sidebar:
        st.markdown("**AI settings**")
        model = st.selectbox("Groq model", ai.MODELS, index=0)
        if not key:
            typed = st.text_input("Groq API key (this session only)", type="password",
                                  help="Better: add GROQ_API_KEY in Streamlit secrets - see README.")
            if typed:
                st.session_state["groq_key_typed"] = typed.strip()
                key = typed.strip()

    if not key:
        st.warning("No Groq API key found. Add **GROQ_API_KEY** to Streamlit secrets (see the README / instructions), "
                   "or paste a key in the sidebar for this session.")
        st.code('GROQ_API_KEY = "gsk_your_key_here"', language="toml")
        return

    try:
        from groq import Groq
    except ImportError:
        st.error("The 'groq' package is not installed. Make sure requirements.txt contains 'groq' and reboot the app.")
        return

    file_hash = hashlib.md5(repr(sorted((k, v.shape) for k, v in S.items())).encode()).hexdigest()
    context = ai.build_context(S, file_hash)
    client = Groq(api_key=key)

    if "chat" not in st.session_state:
        st.session_state.chat = []
    c1, c2 = st.columns([4, 1])
    with c1:
        pick = st.selectbox("Example questions", ["—"] + EXAMPLES, index=0)
    with c2:
        if st.button("Clear chat"):
            st.session_state.chat = []

    for m in st.session_state.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    question = st.chat_input("Ask about costs, rent, contractor, cash flow, solar, drawings ...")
    if not question and pick != "—" and st.button("Ask this example"):
        question = pick
    if not question:
        return

    st.session_state.chat.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    messages = [{"role": "system", "content": ai.SYSTEM_PROMPT + context}] + st.session_state.chat[-8:]
    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(_stream(client, model, messages))
        except Exception as exc:
            msg = str(exc)
            if "401" in msg or "invalid_api_key" in msg.lower():
                st.error("Groq rejected the API key (401). Check the key in your secrets.")
            elif "429" in msg:
                st.error("Groq rate limit reached (429). Wait a minute or try the smaller model.")
            elif "model" in msg.lower() and ("not found" in msg.lower() or "decommission" in msg.lower() or "access" in msg.lower()):
                st.error(f"This model is not available to your Groq account: {msg}. Pick the other model in the sidebar.")
            else:
                st.error(f"Groq request failed: {msg}")
            return
    st.session_state.chat.append({"role": "assistant", "content": answer if isinstance(answer, str) else str(answer)})
