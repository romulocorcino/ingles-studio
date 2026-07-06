"""Study plan: exam date, daily goals, phases, and weight×gap priorities."""
import datetime as dt

import pandas as pd
import streamlit as st

from core import analytics, ui
from core.content import EXAM_DEFAULT_DATE, EXAM_QUESTIONS, EXAM_SESSION_MIN, TOPIC_WEIGHTS
from core.db import cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
settings = st.session_state.get("settings", {})

st.title("📅 Study plan")

# ---------------- settings ----------------
with st.form("plano_form"):
    c1, c2 = st.columns(2)
    exam_date = c1.date_input(
        "Fluency goal date",
        value=dt.date.fromisoformat(settings["exam_date"]) if settings.get("exam_date") else EXAM_DEFAULT_DATE)
    retention = c2.slider("FSRS target retention", 0.80, 0.95,
                          float(settings.get("retention") or 0.90), 0.01,
                          help="Higher retention = shorter intervals = more reviews/day.")
    c3, c4 = st.columns(2)
    daily_goal = c3.number_input("Questions/day goal", 5, 120,
                                 int(settings.get("daily_goal") or 20), 5)
    daily_new = c4.number_input("New cards/day (FSRS)", 0, 60,
                                int(settings.get("daily_new") or 10), 5)
    if st.form_submit_button("💾 Save", type="primary"):
        store.save_settings(user, {"exam_date": exam_date.isoformat(), "retention": retention,
                                   "daily_goal": int(daily_goal), "daily_new": int(daily_new)})
        st.session_state["settings"] = store.get_settings(user)
        st.success("Plan saved ✓")

days_left = max(0, (exam_date - dt.date.today()).days)
st.divider()

# ---------------- phases ----------------
st.subheader(f"🗓️ **{days_left} days** to go — current phase")
phases = [
    ("📖 Foundation", days_left > 90,
     "Cover the curriculum: learn new cards every day, keep the FSRS queue at zero, "
     "practice questions on the week's topic."),
    ("🔁 Consolidation", 30 < days_left <= 90,
     "Curriculum covered: reviews on schedule, adaptive practice on weaknesses, "
     "one partial mock per week."),
    ("📝 Final stretch", days_left <= 30,
     "Full mocks at exam pace (2×/week), error notebook at zero, "
     "heavy review of grammar and your weakest skills."),
]
for name, active, desc in phases:
    if active:
        st.success(f"**{name} (current phase)** — {desc}")
    else:
        st.caption(f"{name} — {desc}")

st.info(f"ℹ️ Timed level test: **{EXAM_QUESTIONS} questions** at conversation pace. "
        "Do one every week or two to see your level climb.")

st.divider()

# ---------------- priorities ----------------
st.subheader("🎯 Where to invest your next hours (skill weight × your gap)")
progress = store.get_progress(user)
answers = store.get_answers(user)
rd = analytics.readiness(cards, progress, answers)

rows = []
for t in TOPIC_WEIGHTS:
    d = rd["topics"][t]
    gap = d["weight"] * (1 - d["score"])
    rows.append({"Topic": t, "Weight": d["weight"], "Readiness": d["score"],
                 "Priority": gap, "Cards in deck": d["cards"]})
pdf = pd.DataFrame(rows).sort_values("Priority", ascending=False)
pdf["Weight"] = (100 * pdf["Weight"]).round(1)
st.dataframe(
    pdf, hide_index=True, use_container_width=True,
    column_config={
        "Weight": st.column_config.NumberColumn(format="%.1f%%"),
        "Readiness": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
        "Priority": st.column_config.ProgressColumn(
            format="%.3f", min_value=0, max_value=float(pdf["Priority"].max() or 1)),
    })
top3 = pdf.head(3)["Topic"].tolist()
st.markdown("**This week's suggestion:** focus reviews and practice on " +
            ", ".join(f"**{t}**" for t in top3) + ".")
