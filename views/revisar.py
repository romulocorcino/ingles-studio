"""FSRS review: due + new queue, predicted-interval buttons, undo, suspend."""
import datetime as dt
import os
import time

import streamlit as st

from core import scheduler, ui
from core.db import APP_DIR, cached_cards, get_store
from core.db import user_cards

store = get_store()
user = st.session_state["user"]
cards = user_cards(user)
settings = st.session_state.get("settings", {})
retention = float(settings.get("retention") or 0.9)
daily_new = int(settings.get("daily_new") or 10)
ss = st.session_state

st.title("🔁 Concept review — spaced repetition (FSRS)")
st.caption("This is your **content-memorization habit**: flashcards and concepts. "
           "Question drills live in 🎯 Practice and 📒 Mistakes notebook.")

if not cards:
    st.warning("No cards. Sync the deck in ⚙️ Data & sync.")
    st.stop()

by_id = {c["id"]: c for c in cards}
topics = sorted({c["topico"] for c in cards})


def build_queue(sel_topic, sel_type, include_new):
    progress = store.get_progress(user)
    pool = [c for c in cards
            if (sel_topic == "All" or c["topico"] == sel_topic)
            and (sel_type == "All" or
                 (sel_type == "Questions" and c["tipo"] == "questao") or
                 (sel_type == "Flashcards" and c["tipo"] != "questao"))]
    learning, review_due, new = [], [], []
    for c in pool:
        p = progress.get(c["id"])
        if p and p.get("suspended"):
            continue
        if not p:
            new.append(c["id"])
        elif scheduler.is_due(p):
            (learning if p.get("state") in ("learning", "relearning") else review_due).append(c["id"])
    queue = learning + review_due
    if include_new:
        queue += new[:daily_new]
    return queue, progress


# ---------------- session setup ----------------
if "rv" not in ss:
    st.markdown("Build your queue: **due cards first**, then new ones (daily limit set in Study plan).")
    c1, c2, c3 = st.columns(3)
    sel_topic = c1.selectbox("Topic", ["All"] + topics)
    sel_type = c2.selectbox("Type", ["Flashcards", "Questions", "All"],
                            help="Default is flashcards/concepts — questions are better trained "
                                 "in Practice (adaptive) and the Error notebook.")
    include_new = c3.toggle("Include new cards", value=True)
    queue, progress = build_queue(sel_topic, sel_type, include_new)
    st.info(f"Queue: **{len(queue)} cards** "
            f"(target retention {retention:.0%}, new/day {daily_new}).")
    if st.button("▶️ Start session", type="primary", disabled=not queue):
        ss.rv = {"queue": queue, "i": 0, "show": False, "counts": {"again": 0, "hard": 0, "good": 0, "easy": 0},
                 "start": time.time(), "card_start": time.time(), "undo": None, "progress": progress}
        st.rerun()
    st.stop()

rv = ss.rv
queue = rv["queue"]

# ---------------- session finished ----------------
if rv["i"] >= len(queue):
    total = sum(rv["counts"].values())
    mins = (time.time() - rv["start"]) / 60
    st.success(f"🏁 Session complete: **{total} reviews** in {mins:.1f} min.")
    c = st.columns(4)
    for col, (k, lbl) in zip(c, [("again", "❌ Again"), ("hard", "😖 Hard"),
                                 ("good", "🙂 Good"), ("easy", "😎 Easy")]):
        col.metric(lbl, rv["counts"][k])
    st.markdown("**Next up:**")
    n1, n2 = st.columns(2)
    with n1:
        st.page_link("views/praticar.py", label="Practice questions →", icon="🎯")
    with n2:
        st.page_link("views/dashboard.py", label="Back to dashboard →", icon="🏠")
    if st.button("🔄 New session"):
        del ss.rv
        st.rerun()
    st.stop()

card = by_id[queue[rv["i"]]]
prog = rv["progress"].get(card["id"])

# ---------------- header ----------------
left, right = st.columns([3, 1])
with left:
    st.progress(rv["i"] / len(queue), text=f"Card {rv['i'] + 1} of {len(queue)}")
with right:
    if rv["undo"] and st.button("↩️ Undo"):
        cid, prev = rv["undo"]
        if prev is None:
            # card was new: restore default state (counts as new again)
            store.upsert_progress(user, cid, scheduler.default_state())
            rv["progress"].pop(cid, None)
        else:
            store.upsert_progress(user, cid, prev)
            rv["progress"][cid] = prev
        rv["i"] = max(0, rv["i"] - 1)
        rv["show"], rv["undo"] = False, None
        st.rerun()

state_lbl = {"new": ("NEW", "blue"), "learning": ("LEARNING", "amber"),
             "relearning": ("RELEARNING", "red"), "review": ("REVIEW", "green")}
stt, color = state_lbl.get((prog or {}).get("state", "new"), ("NEW", "blue"))
meta = (ui.badge(stt, color) + ui.badge(card["topico"]) +
        ui.badge(card.get("subtopico") or "") +
        (ui.badge(f"stability {prog['stability']:.0f}d") if prog and prog.get("stability") else ""))

# ---------------- front / back ----------------
if card["tipo"] == "questao":
    ui.card_box(meta, card["enunciado"])
    choice = st.radio("Choices:", card["opcoes"], index=None,
                      key=f"rv_ch_{rv['i']}", label_visibility="collapsed")
    if not rv["show"]:
        conf = st.radio("How confident are you?", ui.CONF_OPTS, horizontal=True,
                        key=f"rv_cf_{rv['i']}")
        if st.button("Show answer", type="primary", disabled=choice is None, width="stretch"):
            ok = card["opcoes"].index(choice) == card["correta"]
            store.log_answer(user, card["id"], card["topico"], ok, "review",
                             int((time.time() - rv["card_start"]) * 1000),
                             confidence="sure" if conf == ui.CONF_OPTS[0] else "unsure")
            rv["show"], rv["was_ok"] = True, ok
            st.rerun()
    else:
        correct = f"{chr(65 + card['correta'])}) {card['opcoes'][card['correta']]}"
        (st.success if rv.get("was_ok") else st.error)(
            "✅ Correct!" if rv.get("was_ok") else "❌ Missed.")
        ui.answer_box(f"✅ **Answer:** {correct}"
                      + (f"\n\n💡 {card['explicacao']}" if card.get("explicacao") else ""))
        ui.ai_explain(card, key_suffix=str(rv["i"]))
else:
    ui.card_box(meta, f"**{card['frente']}**")
    ui.speak_button(card["frente"], label="🔊 Listen (native)")
    if not rv["show"]:
        feynman = st.text_area(
            "🧑‍🏫 Feynman: explain it in your own words before revealing (optional)",
            key=f"rv_fy_{rv['i']}", height=90,
            placeholder="Writing your own explanation strengthens memory far more than re-reading...")
        if st.button("👁️ Show answer", type="primary", width="stretch"):
            rv["show"] = True
            rv["feynman"] = feynman.strip()
            st.rerun()
    else:
        if rv.get("feynman"):
            ui.answer_box(rv["feynman"], prefix="🧑‍🏫 Your explanation")
        ui.answer_box(card["verso"], prefix="✅ Model answer")
        ui.ai_explain(card, key_suffix=str(rv["i"]))
        if card.get("imagem"):
            img_path = os.path.join(APP_DIR, card["imagem"])
            if os.path.exists(img_path):
                st.image(img_path, width="stretch")

# ---------------- rating buttons (with predicted interval) ----------------
if rv["show"]:
    st.caption("How well did you remember? *(intervals grow automatically: "
               "Good ≈ 10m → 1d → 3d → 8d → 20d → 45d...)*")
    ivs = scheduler.preview_intervals(prog, retention)
    cols = st.columns(4)
    labels = [("again", "❌ Again"), ("hard", "😖 Hard"), ("good", "🙂 Good"), ("easy", "😎 Easy")]
    for col, (rt, lbl) in zip(cols, labels):
        if col.button(f"{lbl}\n\n`{ivs[rt]}`", key=f"rt_{rt}"):
            prev = dict(prog) if prog else None
            new_state = scheduler.review(prog, rt, retention)
            store.upsert_progress(user, card["id"], new_state)
            store.log_review(user, card["id"], rt, (prog or {}).get("state", "new"),
                             new_state, int((time.time() - rv["card_start"]) * 1000))
            rv["progress"][card["id"]] = new_state
            rv["counts"][rt] += 1
            rv["undo"] = (card["id"], prev)
            # learning steps come back later in this same session
            if new_state["state"] in ("learning", "relearning"):
                rv["queue"].append(card["id"])
            rv["i"] += 1
            rv["show"] = False
            rv["card_start"] = time.time()
            st.rerun()

    with st.expander("⚙️ Card options"):
        st.caption("⏩ **I already know this** — push it far out (skips the learning steps):")
        pcols = st.columns(4)
        for col, days in zip(pcols, (3, 7, 30, 90)):
            if col.button(f"{days}d", key=f"push_{days}"):
                s = dict(prog) if prog else scheduler.default_state()
                s["state"] = "review"
                s["step"] = 0
                s["stability"] = max(float(s.get("stability") or 0), float(days))
                s["difficulty"] = s.get("difficulty") or 3.0
                s["due"] = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=days)).isoformat()
                s["last"] = dt.datetime.now(dt.timezone.utc).isoformat()
                s["suspended"] = False
                store.upsert_progress(user, card["id"], s)
                rv["progress"][card["id"]] = s
                rv["queue"].pop(rv["i"])
                rv["show"] = False
                st.rerun()
        if st.button("⏸️ Suspend this card"):
            s = dict(prog) if prog else scheduler.default_state()
            s["suspended"] = True
            store.upsert_progress(user, card["id"], s)
            rv["queue"].pop(rv["i"])
            rv["show"] = False
            st.rerun()
        st.divider()
        st.caption("🚩 **Something wrong with this card?** Flag it for review "
                   "(wrong answer, confusing, typo).")
        fcol1, fcol2 = st.columns([3, 1])
        reason = fcol1.text_input("Reason (optional)", key=f"flag_r_{rv['i']}",
                                  label_visibility="collapsed", placeholder="what's wrong?")
        if fcol2.button("🚩 Flag", key=f"flag_{rv['i']}"):
            store.log_flag(user, card["id"], reason.strip() or "flagged")
            st.toast("Card flagged for review ✓")
