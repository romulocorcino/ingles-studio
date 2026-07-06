"""Question practice: random or adaptive (focuses where you miss most)."""
import random

import streamlit as st

from core import analytics, ui
from core.db import cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
ss = st.session_state

st.title("🎯 Practice questions")

questions = [c for c in cards if c["tipo"] == "questao"]
if not questions:
    st.warning("No questions in the deck.")
    st.stop()

if "pratica" not in ss:
    topics = sorted({c["topico"] for c in questions})
    c1, c2 = st.columns(2)
    sel_topic = c1.selectbox("Topic", ["All"] + topics)
    mode = c2.selectbox("Mode", ["🧠 Adaptive (targets weaknesses)", "🎲 Random"])
    c3, c4 = st.columns(2)
    dif = c3.select_slider("Difficulty", options=["All", "1-2 (easy)", "3", "4-5 (hard)"], value="All")
    pool = [c for c in questions if sel_topic in ("All", c["topico"])]
    if dif == "1-2 (easy)":
        pool = [c for c in pool if c.get("dificuldade", 3) <= 2]
    elif dif == "3":
        pool = [c for c in pool if c.get("dificuldade", 3) == 3]
    elif dif == "4-5 (hard)":
        pool = [c for c in pool if c.get("dificuldade", 3) >= 4]
    if len(pool) <= 5:
        n = len(pool)
        c4.metric("Questions", n)
    else:
        n = c4.slider("Number of questions", 5, len(pool), min(10, len(pool)))

    st.caption(f"{len(pool)} questions available with this filter.")
    if st.button("▶️ Start", type="primary", disabled=not pool):
        if mode.startswith("🧠"):
            answers = store.get_answers(user)
            df = analytics.answers_df(answers)
            # per-card weight: recent misses weigh more; never-seen get medium-high weight
            weights = []
            for c in pool:
                h = df[df["card_id"] == c["id"]].tail(5) if not df.empty else None
                if h is None or h.empty:
                    weights.append(2.0)          # never seen
                else:
                    err = 1 - h["ok"].mean()
                    weights.append(0.5 + 3.0 * err)  # the more you miss, the more it shows up
            chosen = []
            pool2, w2 = pool[:], weights[:]
            for _ in range(min(n, len(pool2))):
                i = random.choices(range(len(pool2)), weights=w2, k=1)[0]
                chosen.append(pool2.pop(i)); w2.pop(i)
        else:
            chosen = random.sample(pool, min(n, len(pool)))
        ss.pratica = ui.new_quiz_state(chosen)
        st.rerun()
    st.stop()

ui.run_quiz_session(store, user, "pratica", "practice")
