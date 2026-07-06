"""Mock exam in real exam format: live timer (90s/question), question navigator,
flag for review, per-topic scoring and MPS comparison."""
import datetime as dt
import random
import time

import pandas as pd
import streamlit as st

from core import ui
from core.content import MPS_BAND, SECONDS_PER_QUESTION
from core.db import cached_cards, get_store

store = get_store()
user = st.session_state["user"]
cards = cached_cards()
ss = st.session_state

st.title("📝 Timed level test")

questions = [c for c in cards if c["tipo"] == "questao"]
if not questions:
    st.warning("No questions in the deck.")
    st.stop()

# ============================================================ setup
if "mock" not in ss:
    st.markdown(
        f"A timed challenge to measure your level: **~{SECONDS_PER_QUESTION}s per question** "
        f"for fast recognition, like real conversation.")
    topics = sorted({c["topico"] for c in questions})
    c1, c2 = st.columns(2)
    sel = c1.selectbox("Topic", ["All"] + topics)
    pool = [c for c in questions if sel in ("All", c["topico"])]
    n_opts = sorted({x for x in (5, 10, 20, 30, 45, 60, 90) if x <= len(pool)} | {len(pool)})
    if len(n_opts) < 2:
        n = n_opts[0] if n_opts else len(pool)
        c2.metric("Questions", n)
    else:
        n = c2.select_slider("Number of questions", options=n_opts, value=n_opts[-1])
    limit_min = n * SECONDS_PER_QUESTION / 60
    st.caption(f"{len(pool)} questions available · time limit: **{limit_min:.0f} min**")
    if st.button("▶️ Start test", type="primary", disabled=not pool):
        qs = random.sample(pool, min(n, len(pool)))
        ss.mock = {"qs": qs, "i": 0, "ans": {}, "flags": set(),
                   "start": time.time(), "limit_s": len(qs) * SECONDS_PER_QUESTION,
                   "submitted": False, "confirm_end": False}
        st.rerun()
    st.stop()

m = ss.mock
qs = m["qs"]
n = len(qs)


def _submit():
    m["submitted"] = True
    m["duration_s"] = int(time.time() - m["start"])


# ============================================================ running
if not m["submitted"]:

    @st.fragment(run_every="1s")
    def timer():
        left = m["limit_s"] - (time.time() - m["start"])
        if left <= 0:
            _submit()
            st.rerun(scope="app")
        mm, sc = divmod(int(left), 60)
        cls = "mock-timer low" if left < 120 else "mock-timer"
        st.markdown(f'<div class="{cls}">⏱ {mm:02d}:{sc:02d}</div>', unsafe_allow_html=True)

    top1, top2, top3 = st.columns([2, 1, 1])
    with top1:
        answered = len([v for v in m["ans"].values() if v is not None])
        st.progress(answered / n, text=f"{answered}/{n} answered · {len(m['flags'])} flagged 🚩")
    with top2:
        timer()
    with top3:
        if st.button("🏁 Finish", type="primary", use_container_width=True):
            m["confirm_end"] = True

    if m["confirm_end"]:
        blank = n - len([v for v in m["ans"].values() if v is not None])
        msg = f"**{blank} questions still blank**. " if blank else ""
        st.warning(f"{msg}Submit your test?")
        cc1, cc2 = st.columns(2)
        if cc1.button("✅ Submit now", use_container_width=True):
            _submit()
            st.rerun()
        if cc2.button("← Back to the test", use_container_width=True):
            m["confirm_end"] = False
            st.rerun()
        st.stop()

    # ---------- question navigator ----------
    per_row = 10
    for start in range(0, n, per_row):
        cols = st.columns(per_row)
        for j, col in enumerate(cols):
            idx = start + j
            if idx >= n:
                break
            mark = "🚩" if idx in m["flags"] else ("●" if m["ans"].get(idx) is not None else "○")
            if col.button(f"{mark}{idx + 1}", key=f"nav_{idx}",
                          type="primary" if idx == m["i"] else "secondary"):
                m["i"] = idx
                st.rerun()

    # ---------- current question ----------
    i = m["i"]
    c = qs[i]
    ui.card_box(f"Question {i + 1} of {n} · {c['topico']}", c["enunciado"])
    prev_choice = m["ans"].get(i)
    choice = st.radio("Choices:", c["opcoes"],
                      index=prev_choice if prev_choice is not None else None,
                      key=f"mock_ch_{i}", label_visibility="collapsed")
    m["ans"][i] = c["opcoes"].index(choice) if choice is not None else m["ans"].get(i)

    b1, b2, b3 = st.columns(3)
    if b1.button("← Previous", disabled=i == 0, use_container_width=True):
        m["i"] -= 1
        st.rerun()
    flag_lbl = "🚩 Unflag" if i in m["flags"] else "🚩 Flag for review"
    if b2.button(flag_lbl, use_container_width=True):
        m["flags"] ^= {i}
        st.rerun()
    if b3.button("Next →", disabled=i == n - 1, use_container_width=True):
        m["i"] += 1
        st.rerun()
    st.stop()

# ============================================================ results
correct, by_t = 0, {}
for idx, c in enumerate(qs):
    sel_i = m["ans"].get(idx)
    ok = sel_i is not None and sel_i == c["correta"]
    correct += 1 if ok else 0
    by_t.setdefault(c["topico"], [0, 0])
    by_t[c["topico"]][1] += 1
    by_t[c["topico"]][0] += 1 if ok else 0

pct = correct / n
dur = m.get("duration_s", int(time.time() - m["start"]))

if not m.get("logged"):
    for idx, c in enumerate(qs):
        sel_i = m["ans"].get(idx)
        ok = sel_i is not None and sel_i == c["correta"]
        store.log_answer(user, c["id"], c["topico"], ok, "mock", None)
    store.log_mock(user, {"n": n, "correct": correct, "pct": round(100 * pct, 1),
                          "duration_s": dur,
                          "detail": {t: {"ok": o, "total": tt} for t, (o, tt) in by_t.items()}})
    m["logged"] = True

st.subheader("🏁 Results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Score", f"{100 * pct:.0f}%", f"{correct}/{n}")
c2.metric("Time", f"{dur // 60}min {dur % 60}s")
c3.metric("Pace", f"{dur / n:.0f}s/question")
mps_lo, mps_hi = MPS_BAND
if pct >= mps_hi:
    verdict, help_ = "✅ Fluent range", "At/above the functional-fluency target (70–80%)."
elif pct >= mps_lo:
    verdict, help_ = "⚠️ Almost there", "Inside the target band (70–80%) — keep going."
else:
    verdict, help_ = "❌ Keep practicing", "Below the 70–80% fluency target."
c4.metric("vs. target", verdict, help=help_)

st.subheader("By topic")
df = pd.DataFrame([{"Topic": t, "Correct": f"{o}/{tt}", "Accuracy": o / tt}
                   for t, (o, tt) in sorted(by_t.items(), key=lambda x: x[1][0] / x[1][1])])
st.dataframe(df, hide_index=True, use_container_width=True,
             column_config={"Accuracy": st.column_config.ProgressColumn(
                 format="percent", min_value=0, max_value=1)})

filt = st.radio("Question review:", ["Misses only", "Flagged 🚩", "All"], horizontal=True)
for idx, c in enumerate(qs):
    sel_i = m["ans"].get(idx)
    ok = sel_i is not None and sel_i == c["correta"]
    if filt == "Misses only" and ok:
        continue
    if filt == "Flagged 🚩" and idx not in m["flags"]:
        continue
    with st.expander(f"{'✅' if ok else '❌'} Q{idx + 1} · {c['topico']} — {c['enunciado'][:70]}"):
        st.markdown(c["enunciado"])
        st.markdown(f"Your answer: **{c['opcoes'][sel_i] if sel_i is not None else '(blank)'}**")
        st.markdown(f"Correct: **{chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}**")
        if c.get("explicacao"):
            st.markdown(f"💡 {c['explicacao']}")

if st.button("🔄 New test", type="primary"):
    del ss.mock
    st.rerun()
