"""Error notebook: any question whose LAST answer was wrong stays here
until you answer it correctly again. Missed 2+ times = HARD, drilled first."""
import pandas as pd
import plotly.express as px
import streamlit as st

from core import analytics, ui
from core.db import cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
ss = st.session_state

st.title("📒 Error notebook")
st.caption("Your **real-use habit**, part 2: turn every miss into a point. "
           "Concepts live in 🔁 Concept review.")

answers = store.get_answers(user)
notebook = analytics.error_notebook(cards, answers)
hard = [e for e in notebook if e["hard"]]
lucky = [e for e in notebook if e.get("lucky")]

if "erros_qz" in ss:
    ui.run_quiz_session(store, user, "erros_qz", "errors")
    st.stop()

if not notebook:
    st.success("🎉 Notebook is empty — no questions pending. "
               "Miss one in Practice/Test? It shows up here automatically.")
    st.page_link("views/praticar.py", label="Practice questions →", icon="🎯")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Pending questions", len(notebook))
c2.metric("🔥 Hard (missed 2+ times)", len(hard))
c3.metric("🍀 Lucky guesses", len(lucky),
          help="Answered correctly but flagged as a guess — you don't truly know these yet.")

b1, b2 = st.columns(2)
if b1.button(f"▶️ Drill all {len(notebook)}", type="primary", use_container_width=True):
    ss.erros_qz = ui.new_quiz_state([e["card"] for e in notebook])
    st.rerun()
if b2.button(f"🔥 Drill only the {len(hard)} hard ones", disabled=not hard,
             use_container_width=True):
    ss.erros_qz = ui.new_quiz_state([e["card"] for e in hard])
    st.rerun()

tab_stats, tab_list = st.tabs(["📉 What I miss most", "📋 Full list by topic"])

# ---------------- what I miss most (reinforcement focus) ----------------
with tab_stats:
    weak = analytics.weakest_topics(answers)
    missed = analytics.most_missed(cards, answers)

    if weak:
        st.subheader("🎯 Weakest topics (by total misses)")
        wdf = pd.DataFrame([{"Topic": w["topic"], "Misses": w["misses"],
                             "Attempts": w["attempts"], "Accuracy": w["acc"]} for w in weak])
        fig = px.bar(wdf, x="Misses", y="Topic", orientation="h", text="Misses",
                     color="Accuracy", color_continuous_scale=["#f85149", "#d29922", "#2ea043"],
                     range_color=[0.3, 0.9])
        fig.update_traces(textposition="outside")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#c9d1d9", coloraxis_showscale=False,
                          height=max(240, 42 * len(wdf)), margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
        worst = weak[0]["topic"]
        worst_cards = [c for c in cards if c["tipo"] == "questao" and c["topico"] == worst]
        if st.button(f"🎯 Drill your worst topic: {worst} ({weak[0]['misses']} misses)",
                     type="primary"):
            import random
            picks = ([e["card"] for e in missed if e["card"]["topico"] == worst]
                     or random.sample(worst_cards, min(15, len(worst_cards))))
            ss.erros_qz = ui.new_quiz_state(picks[:20])
            st.rerun()

    if missed:
        st.subheader("❌ Your most-missed questions")
        st.caption("Ranked by how many times you got them wrong — these deserve the most reps.")
        for e in missed[:15]:
            c = e["card"]
            st.markdown(
                f"**×{e['misses']}** missed ({e['misses']}/{e['attempts']} attempts) · "
                f"`{c['topico']}`  \n{c['enunciado'][:120]}  \n"
                f"✅ *{chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}*")
            st.markdown("<hr style='margin:.3rem 0;opacity:.15'>", unsafe_allow_html=True)
    else:
        st.info("Once you miss questions, your worst offenders show up here ranked by miss count.")

# ---------------- full list by topic ----------------
with tab_list:
    by_topic = {}
    for e in notebook:
        by_topic.setdefault(e["card"]["topico"], []).append(e)
    for t in sorted(by_topic, key=lambda x: -len(by_topic[x])):
        n_hard = sum(1 for e in by_topic[t] if e["hard"])
        label = f"**{t}** — {len(by_topic[t])} pending" + (f" · 🔥 {n_hard} hard" if n_hard else "")
        with st.expander(label, expanded=len(by_topic) <= 3):
            for e in by_topic[t]:
                c = e["card"]
                fire = f"🔥 ×{e['misses']} " if e["hard"] else ("🍀 " if e.get("lucky") else "")
                st.markdown(f"- {fire}{c['enunciado'][:110]}  \n"
                            f"  ✅ *{chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}*")
