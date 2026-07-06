"""Library: the whole deck at a glance — scan to memorize fast, and batch-manage
what should show up more (bring to today) or less (skip) in your reviews."""
import datetime as dt
import os

import pandas as pd
import streamlit as st

from core import scheduler, ui
from core.content import TOPIC_ABBREV
from core.db import APP_DIR, cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
UTC = dt.timezone.utc

st.title("📖 Library — the whole deck at a glance")

if not cards:
    st.warning("No cards. Sync the deck in ⚙️ Data & sync.")
    st.stop()

progress = store.get_progress(user)
topics = sorted({c["topico"] for c in cards})

tab_scan, tab_manage = st.tabs(["📖 Scan mode", "🛠️ Manage frequency"])


def _content(c):
    return c.get("enunciado") or c.get("frente") or ""


def _answer(c):
    if c["tipo"] == "questao":
        return f"{chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}"
    return c.get("verso") or ""


def _state_chip(p):
    if not p:
        return ui.badge("NEW", "blue")
    if p.get("suspended"):
        return ui.badge("SKIPPED", "red")
    s = p.get("state", "new").upper()
    color = {"REVIEW": "green", "LEARNING": "amber", "RELEARNING": "red"}.get(s, "blue")
    extra = f" · {p['stability']:.0f}d" if p.get("stability") else ""
    return ui.badge(s + extra, color)


# ============================================================ scan mode
with tab_scan:
    c1, c2, c3 = st.columns([1.2, 1, 1.5])
    sel_topic = c1.selectbox("Topic", ["All"] + topics, key="lib_topic")
    sel_type = c2.selectbox("Type", ["All", "Concepts", "Questions"], key="lib_type")
    q = c3.text_input("🔎 Search", key="lib_q", placeholder="duration, DuPont, put-call...")
    hide = st.toggle("🙈 Hide answers (self-test while scanning)", value=False)

    ql = q.strip().lower()
    pool = [c for c in cards
            if (sel_topic == "All" or c["topico"] == sel_topic)
            and (sel_type == "All"
                 or (sel_type == "Questions" and c["tipo"] == "questao")
                 or (sel_type == "Concepts" and c["tipo"] != "questao"))
            and (not ql or ql in (_content(c) + " " + _answer(c) + " "
                                  + (c.get("explicacao") or "")).lower())]
    st.caption(f"**{len(pool)} cards** in view")

    groups = {}
    for c in pool:
        groups.setdefault((c["topico"], c.get("subtopico") or "General"), []).append(c)

    for (t, sub), cs in sorted(groups.items()):
        expanded = bool(ql) or sel_topic != "All"
        with st.expander(f"**{TOPIC_ABBREV.get(t, t)} · {sub}** ({len(cs)})", expanded=expanded):
            for c in cs:
                p = progress.get(c["id"])
                icon = "❓" if c["tipo"] == "questao" else "💡"
                st.markdown(f"{icon} **{_content(c)}** {_state_chip(p)}",
                            unsafe_allow_html=True)
                if not hide:
                    st.markdown(f"→ {_answer(c)}")
                    if c["tipo"] == "questao" and c.get("explicacao"):
                        st.caption(c["explicacao"])
                    if c.get("imagem"):
                        img_path = os.path.join(APP_DIR, c["imagem"])
                        if os.path.exists(img_path):
                            st.image(img_path, width=520)
                st.markdown("<hr style='margin:.4rem 0;opacity:.15'>", unsafe_allow_html=True)

# ============================================================ manage frequency
with tab_manage:
    st.markdown(
        "Batch-tune your review load: **⏸️ Skip** removes a card from all queues; "
        "**🔜 Today** brings it into today's review queue; **⏩ 30d** marks it as "
        "well-known and pushes it a month out (skipping the learning steps).")

    m1, m2 = st.columns(2)
    m_topic = m1.selectbox("Topic", ["All"] + topics, key="mng_topic")
    m_state = m2.selectbox("Status", ["All", "New", "Learning", "Review", "Skipped"], key="mng_state")

    rows = []
    for c in cards:
        if m_topic != "All" and c["topico"] != m_topic:
            continue
        p = progress.get(c["id"])
        state = "Skipped" if (p and p.get("suspended")) else (p.get("state", "new") if p else "new")
        state_lbl = {"new": "New", "learning": "Learning", "relearning": "Learning",
                     "review": "Review", "Skipped": "Skipped"}.get(state, state)
        if m_state != "All" and state_lbl != m_state:
            continue
        rows.append({
            "id": c["id"],
            "Topic": TOPIC_ABBREV.get(c["topico"], c["topico"]),
            "T": "Q" if c["tipo"] == "questao" else "C",
            "Content": _content(c)[:85],
            "Status": state_lbl,
            "Stab. (d)": round(p.get("stability") or 0) if p else 0,
            "⏸️ Skip": bool(p and p.get("suspended")),
            "🔜 Today": False,
            "⏩ 30d": False,
        })

    if not rows:
        st.info("Nothing matches this filter.")
    else:
        df = pd.DataFrame(rows)
        edited = st.data_editor(
            df, hide_index=True, use_container_width=True, height=430, key="mng_editor",
            disabled=["id", "Topic", "T", "Content", "Status", "Stab. (d)"],
            column_config={
                "id": None,
                "T": st.column_config.TextColumn(width="small", help="Q = question, C = concept"),
                "⏸️ Skip": st.column_config.CheckboxColumn(help="Remove from all queues"),
                "🔜 Today": st.column_config.CheckboxColumn(help="Bring into today's review queue"),
                "⏩ 30d": st.column_config.CheckboxColumn(help="Well-known: push 30 days out"),
            })

        if st.button("💾 Apply changes", type="primary"):
            n_skip = n_unskip = n_today = n_push = 0
            now = dt.datetime.now(UTC)
            now_iso = now.isoformat()
            for _, r in edited.iterrows():
                cid = r["id"]
                p = progress.get(cid)
                was_skipped = bool(p and p.get("suspended"))
                want_skip = bool(r["⏸️ Skip"])
                want_today = bool(r["🔜 Today"])
                want_push = bool(r["⏩ 30d"])
                if want_skip != was_skipped:
                    s = dict(p) if p else scheduler.default_state()
                    s["suspended"] = want_skip
                    store.upsert_progress(user, cid, s)
                    progress[cid] = s
                    n_skip += want_skip
                    n_unskip += (not want_skip)
                if want_today:
                    s = dict(progress.get(cid) or scheduler.default_state())
                    s["due"], s["suspended"] = now_iso, False
                    store.upsert_progress(user, cid, s)
                    progress[cid] = s
                    n_today += 1
                if want_push:
                    s = dict(progress.get(cid) or scheduler.default_state())
                    s["state"], s["step"] = "review", 0
                    s["stability"] = max(float(s.get("stability") or 0), 30.0)
                    s["difficulty"] = s.get("difficulty") or 3.0
                    s["due"] = (now + dt.timedelta(days=30)).isoformat()
                    s["last"], s["suspended"] = now_iso, False
                    store.upsert_progress(user, cid, s)
                    progress[cid] = s
                    n_push += 1
            msgs = []
            if n_skip:
                msgs.append(f"{n_skip} skipped")
            if n_unskip:
                msgs.append(f"{n_unskip} re-activated")
            if n_today:
                msgs.append(f"{n_today} queued for today")
            if n_push:
                msgs.append(f"{n_push} pushed 30d out")
            st.success("Done: " + (", ".join(msgs) if msgs else "no changes") + " ✓")
            if n_today:
                st.page_link("views/revisar.py", label="Start reviewing them →", icon="🔁")
