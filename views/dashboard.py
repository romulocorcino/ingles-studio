"""Dashboard: exam-weighted readiness, today's to-dos, deck coverage."""
import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import analytics, scheduler, ui
from core.content import EXAM_DEFAULT_DATE, TOPIC_ABBREV, TOPIC_WEIGHTS
from core.db import cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
progress = store.get_progress(user)
answers = store.get_answers(user)
settings = st.session_state.get("settings", {})

st.title("🏠 Dashboard")

if not cards:
    st.warning("Card bank is empty — go to **⚙️ Data & sync** and sync the deck.")
    st.stop()

# ---------------- today's KPIs ----------------
concepts = [c for c in cards if c["tipo"] != "questao"]
due_concepts = [c for c in concepts if progress.get(c["id"]) and scheduler.is_due(progress.get(c["id"]))]
new_concepts = [c for c in concepts if not progress.get(c["id"])]
today = dt.date.today()
ans_today = [a for a in answers if str(a.get("ts", ""))[:10] == today.isoformat()]
acc7 = analytics.answers_df(answers)
acc7 = acc7[acc7["date"] >= today - dt.timedelta(days=7)]["ok"].mean() if not acc7.empty else None
notebook = analytics.error_notebook(cards, answers)

rd = analytics.readiness(cards, progress, answers)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🔁 Concepts due", len(due_concepts))
c2.metric("📒 Errors pending", len(notebook))
c3.metric("🎯 Questions today", len(ans_today))
c4.metric("✅ Accuracy (7 days)", ui.fmt_pct(acc7))
c5.metric("🧭 Readiness", ui.fmt_pct(rd["overall"]))

# ---------------- gauge + today's plan ----------------
g1, g2 = st.columns([1, 1.4])
with g1:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=100 * rd["overall"],
        number={"suffix": "%"},
        title={"text": "Fluency readiness by skill", "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#5B8DEF"},
            "steps": [
                {"range": [0, 40], "color": "rgba(248,81,73,.25)"},
                {"range": [40, 70], "color": "rgba(210,153,34,.25)"},
                {"range": [70, 100], "color": "rgba(46,160,67,.25)"}],
            "threshold": {"line": {"color": "#2ea043", "width": 3}, "value": 70},
        }))
    fig.update_layout(height=230, margin=dict(l=25, r=25, t=45, b=5),
                      paper_bgcolor="rgba(0,0,0,0)", font_color="#c9d1d9")
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.subheader("📋 What to do today")
    daily_goal = int(settings.get("daily_goal") or 20)
    daily_new = int(settings.get("daily_new") or 10)

    st.markdown("**🧠 Memorize content** (Concept review)")
    memo = []
    if due_concepts:
        memo.append(f"🔁 Review **{len(due_concepts)} concept cards** due")
    if new_concepts:
        memo.append(f"🆕 Learn **{min(daily_new, len(new_concepts))} new concepts**")
    for t in memo or ["✅ Concept queue is clear"]:
        st.markdown("- " + t)
    if memo:
        st.page_link("views/revisar.py", label="Start concept review →", icon="🔁")

    st.markdown("**📝 Apply in real use** (Practice / Mistakes)")
    apply_ = []
    hard_n = sum(1 for e in notebook if e["hard"])
    if notebook:
        apply_.append(f"📒 Clear **{len(notebook)} questions** from the error notebook"
                      + (f" (🔥 {hard_n} hard)" if hard_n else ""))
    remaining = max(0, daily_goal - len(ans_today))
    if remaining:
        apply_.append(f"🎯 Answer **{remaining} questions** (daily goal: {daily_goal})")
    weak = sorted(((t, d) for t, d in rd["topics"].items()
                   if d["accuracy"] is not None and d["accuracy"] < 0.6 and d["answered"] >= 3),
                  key=lambda x: x[1]["accuracy"])
    if weak:
        apply_.append("🎯 Focus on weak topics: " +
                      ", ".join(f"**{TOPIC_ABBREV[t]}** ({ui.fmt_pct(d['accuracy'])})" for t, d in weak[:3]))
    for t in apply_ or ["🎉 All caught up — try a timed test!"]:
        st.markdown("- " + t)
    lc1, lc2 = st.columns(2)
    with lc1:
        st.page_link("views/erros.py" if notebook else "views/praticar.py",
                     label="Clear errors →" if notebook else "Practice questions →",
                     icon="📒" if notebook else "🎯")
    with lc2:
        st.page_link("views/simulado.py", label="Timed test →", icon="📝")

st.divider()

# ---------------- topic table ----------------
st.subheader("🗺️ Skills — weight × your preparation")
rows = []
for t, (lo, hi) in TOPIC_WEIGHTS.items():
    d = rd["topics"][t]
    rows.append({
        "Topic": t,
        "Weight": f"{lo}–{hi}%",
        "Cards": d["cards"],
        "FSRS maturity": d["maturity"],
        "Accuracy": d["accuracy"] if d["accuracy"] is not None else float("nan"),
        "Readiness": d["score"],
    })
df = pd.DataFrame(rows)
st.dataframe(
    df, hide_index=True, use_container_width=True,
    column_config={
        "FSRS maturity": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
        "Accuracy": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
        "Readiness": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
    })

# ---------------- coverage alerts ----------------
gaps = [t for t, d in rd["topics"].items() if d["cards"] < 15]
if gaps:
    st.warning("📚 **Deck coverage incomplete** — few cards in: " +
               ", ".join(f"{t} ({rd['topics'][t]['cards']})" for t in sorted(gaps, key=lambda x: rd['topics'][x]['cards'])) +
               ". Ask Claude to generate more cards for these skills.")
