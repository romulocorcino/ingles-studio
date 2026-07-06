"""English Studio — Streamlit + Supabase (or local SQLite mode)."""
import datetime as dt
import json
import os

import streamlit as st

from core import analytics, ui
from core.content import EXAM_DEFAULT_DATE
from core.db import cached_cards, clear_card_cache, get_store

st.set_page_config(page_title="English Studio", page_icon="🇬🇧",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

store = get_store()

# ---------------- first run: auto-seed the deck ----------------
if not cached_cards():
    seed_path = os.path.join(os.path.dirname(__file__), "seed_cards.json")
    if os.path.exists(seed_path):
        seed = json.load(open(seed_path, encoding="utf-8"))["cards"]
        store.upsert_cards(seed)
        clear_card_cache()

# ---------------- global sidebar ----------------
with st.sidebar:
    st.title("🇬🇧 English Studio")
    user = st.text_input("👤 User", value=st.session_state.get("user", "romulo"),
                         help="Your progress is saved under this name (syncs across devices with Supabase).")
    st.session_state["user"] = user.strip().lower() or "romulo"
    user = st.session_state["user"]

    settings = store.get_settings(user)
    st.session_state["settings"] = settings
    goal_date = dt.date.fromisoformat(settings["exam_date"]) if settings.get("exam_date") else EXAM_DEFAULT_DATE
    days_left = max(0, (goal_date - dt.date.today()).days)

    answers = store.get_answers(user)
    reviews = store.get_reviews(user)
    stk = analytics.streak(answers, reviews)

    c1, c2 = st.columns(2)
    c1.metric("🎯 Days to goal", days_left)
    c2.metric("🔥 Streak", f"{stk}d")

    mode_txt = ("☁️ Supabase — progress synced across devices" if store.mode == "supabase"
                else "💻 Local mode — data stays on this computer")
    st.caption(mode_txt)

# ---------------- navigation ----------------
pages = {
    "Study": [
        st.Page("views/dashboard.py", title="Dashboard", icon="🏠", default=True),
        st.Page("views/revisar.py", title="Review (spaced repetition)", icon="🔁"),
        st.Page("views/praticar.py", title="Practice", icon="🎯"),
        st.Page("views/simulado.py", title="Timed level test", icon="📝"),
        st.Page("views/erros.py", title="Mistakes notebook", icon="📒"),
    ],
    "Track": [
        st.Page("views/desempenho.py", title="Performance", icon="📊"),
        st.Page("views/plano.py", title="Study plan", icon="📅"),
    ],
    "Reference": [
        st.Page("views/biblioteca.py", title="Library", icon="📖"),
        st.Page("views/referencia.py", title="Grammar reference", icon="📐"),
        st.Page("views/dados.py", title="Data & sync", icon="⚙️"),
    ],
}
st.navigation(pages).run()
