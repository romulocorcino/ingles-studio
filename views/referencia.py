"""Grammar & pronunciation reference: browse + flash-drill mode."""
import random

import streamlit as st

from core.content import FORMULAS

st.title("📐 Grammar & pronunciation reference")
st.caption("Verb tenses, irregular verbs, pronunciation tips and common confusions. "
           "Search or drill yourself.")

tab1, tab2 = st.tabs(["📖 Browse", "🎲 Flash drill"])

with tab1:
    search = st.text_input("🔎 Search", placeholder="e.g., present perfect, irregular, TH...")
    q = search.strip().lower()
    for topic, items in FORMULAS.items():
        vis = [(n, b, o) for n, b, o in items
               if not q or q in n.lower() or q in b.lower() or q in o.lower()]
        if not vis:
            continue
        with st.expander(f"**{topic}** ({len(vis)})", expanded=bool(q)):
            for name, body, note in vis:
                st.markdown(f"**{name}**" + (f"  — *{note}*" if note else ""))
                st.markdown(body)
                st.divider()

with tab2:
    st.caption("You get the topic — recall the rule before revealing it.")
    all_f = [(t, n, b, o) for t, items in FORMULAS.items() for n, b, o in items]
    ss = st.session_state
    if st.button("🎲 Draw a rule", type="primary") or "ref_atual" not in ss:
        ss.ref_atual = random.choice(all_f)
        ss.ref_show = False
    t, n, b, o = ss.ref_atual
    st.markdown(f"### {n}")
    st.caption(t)
    if not ss.get("ref_show"):
        if st.button("👁️ Reveal"):
            ss.ref_show = True
            st.rerun()
    else:
        st.markdown(b)
        if o:
            st.caption(o)
