"""Data: deck sync, card browser, backup/restore and reset."""
import datetime as dt
import json
import os

import pandas as pd
import streamlit as st

from core.db import APP_DIR, cached_cards, clear_card_cache, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()

st.title("⚙️ Data & sync")

mode = ("☁️ **Supabase** — progress synced across devices" if store.mode == "supabase"
        else "💻 **Local mode (SQLite)** — no Supabase configured; data stays on this computer")
st.markdown(f"Current backend: {mode}")
if store.mode == "local":
    st.caption("To sync across devices, set SUPABASE_URL and SUPABASE_KEY "
               "in the Streamlit Secrets (see README).")

st.divider()

# ---------------- deck sync ----------------
st.subheader("🔄 Card deck")
st.markdown(f"Cards in the bank: **{len(cards)}**. The deck is versioned in `seed_cards.json` "
            "in the repository — edit/add cards there and sync here.")
if st.button("🔄 Sync cards from the repository", type="primary"):
    try:
        seed = json.load(open(os.path.join(APP_DIR, "seed_cards.json"), encoding="utf-8"))["cards"]
        store.upsert_cards(seed)
        clear_card_cache()
        st.success(f"Synced {len(seed)} cards ✓")
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

# ---------------- browser ----------------
st.subheader("🗂️ Card browser")
if cards:
    df = pd.DataFrame([{
        "id": c["id"], "type": c["tipo"], "topic": c["topico"],
        "subtopic": c.get("subtopico", ""), "diff": c.get("dificuldade", 3),
        "content": (c.get("enunciado") or c.get("frente") or "")[:90],
    } for c in cards])
    f1, f2 = st.columns(2)
    ft = f1.multiselect("Topic", sorted(df["topic"].unique()))
    fp = f2.multiselect("Type", sorted(df["type"].unique()))
    if ft:
        df = df[df["topic"].isin(ft)]
    if fp:
        df = df[df["type"].isin(fp)]
    st.dataframe(df, hide_index=True, use_container_width=True, height=320)

st.divider()

# ---------------- backup ----------------
st.subheader("💾 Progress backup")
c1, c2 = st.columns(2)
with c1:
    payload = {
        "exported_at": dt.datetime.now().isoformat(),
        "user": user,
        "progress": store.get_progress(user),
        "answers": store.get_answers(user),
        "mocks": store.get_mocks(user),
        "settings": store.get_settings(user),
    }
    st.download_button("⬇️ Export progress (JSON)",
                       json.dumps(payload, ensure_ascii=False, indent=1, default=str),
                       file_name=f"english_backup_{user}_{dt.date.today()}.json",
                       use_container_width=True)
with c2:
    up = st.file_uploader("⬆️ Restore backup", type="json", label_visibility="collapsed")
    if up and st.button("Restore progress from file", use_container_width=True):
        try:
            data = json.load(up)
            for cid, state in (data.get("progress") or {}).items():
                store.upsert_progress(user, cid, state)
            if data.get("settings"):
                s = {k: v for k, v in data["settings"].items()
                     if k in ("exam_date", "retention", "daily_new", "daily_goal")}
                store.save_settings(user, s)
            st.success("Progress restored ✓ (answer/mock history is not overwritten)")
        except Exception as e:
            st.error(f"Invalid backup: {e}")

st.divider()

# ---------------- flagged cards ----------------
st.subheader("🚩 Flagged cards")
flags = store.get_flags(user)
if not flags:
    st.caption("No cards flagged. Hit 🚩 during review if a card looks wrong or confusing.")
else:
    by_id = {c["id"]: c for c in cards}
    st.caption(f"{len(flags)} card(s) you flagged for review:")
    for fl in flags:
        c = by_id.get(fl["card_id"])
        content = (c.get("enunciado") or c.get("frente") or fl["card_id"]) if c else fl["card_id"]
        cc1, cc2 = st.columns([5, 1])
        cc1.markdown(f"**{fl['card_id']}** · {fl.get('reason','')}  \n{content[:120]}")
        if cc2.button("Resolve", key=f"unflag_{fl['card_id']}"):
            store.delete_flag(user, fl["card_id"])
            st.rerun()

st.divider()

# ---------------- reset ----------------
st.subheader("🗑️ Danger zone")
conf = st.checkbox("I understand this permanently deletes my progress")
if st.button("⚠️ Reset all my progress", disabled=not conf):
    store.delete_progress(user)
    store.delete_answers(user)
    store.delete_mocks(user)
    store.delete_reviews(user)
    st.success("Progress reset.")
