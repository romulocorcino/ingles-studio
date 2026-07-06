"""Shared visual components and the reusable practice session."""
import datetime as dt
import json as _json
import time

import streamlit as st
import streamlit.components.v1 as components

CSS = """
<style>
:root {
  --accent: #4C9AFF;
  --surface: #151A23;
  --surface-2: #1C2330;
  --line: rgba(120, 140, 170, .22);
  --ok: #3FB950; --warn: #E3B341; --bad: #F85149;
}

/* ---- general ---- */
.block-container { padding-top: 2.2rem; max-width: 1100px; }
h1 { font-size: 1.55rem !important; letter-spacing: .2px; font-weight: 700; }
h2, h3 { letter-spacing: .2px; }
h1 span, h2 span, h3 span { color: inherit; }
[data-testid="stSidebarUserContent"] .stTextInput input { font-size: .9rem; }

/* hide Streamlit chrome (menu, footer, deploy) — but KEEP the toolbar,
   because the sidebar-expand button lives inside it (mobile needs it!) */
#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbarActions"], [data-testid="stDecoration"],
[data-testid="stMainMenu"], [data-testid="stAppDeployButton"] { display: none; }

/* big, obvious reopen-sidebar button (thumb-friendly on mobile) */
[data-testid="stExpandSidebarButton"] {
  background: var(--accent) !important;
  border-radius: 50%;
  width: 2.6rem; height: 2.6rem;
  min-width: 2.6rem;
  align-items: center; justify-content: center;
  box-shadow: 0 2px 12px rgba(0,0,0,.45);
}
[data-testid="stExpandSidebarButton"] span,
[data-testid="stExpandSidebarButton"] svg { color: #fff !important; fill: #fff !important; }

/* collapse button inside the sidebar: always visible (not only on hover) */
[data-testid="stSidebarCollapseButton"] { display: inline-flex !important; }
[data-testid="stSidebarCollapseButton"] button { visibility: visible !important; }

/* ---- sidebar ---- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #10141C 0%, #0B0E14 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] li a:hover { border-radius: 8px; }

/* ---- metrics as cards ---- */
[data-testid="stMetric"] {
  background: linear-gradient(180deg, var(--surface-2) 0%, var(--surface) 100%);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: .7rem .9rem;
  box-shadow: 0 1px 6px rgba(0,0,0,.25);
}
[data-testid="stMetricValue"] { font-size: 1.45rem; font-weight: 700; }
[data-testid="stMetricLabel"] { opacity: .75; }
[data-testid="stMetricLabel"] p { white-space: normal !important; font-size: .8rem; line-height: 1.2; }

/* ---- study card ---- */
.study-card {
  background: linear-gradient(180deg, var(--surface-2) 0%, var(--surface) 100%);
  border: 1px solid var(--line);
  border-left: 3px solid var(--accent);
  border-radius: 14px;
  padding: 1.4rem 1.6rem;
  margin: .6rem 0 1rem 0;
  font-size: 1.12rem;
  line-height: 1.55;
  box-shadow: 0 2px 10px rgba(0,0,0,.30);
}
.study-card .meta { font-size: .78rem; opacity: .65; margin-bottom: .6rem; }

/* answer container (st.container border) mais suave */
[data-testid="stVerticalBlockBorderWrapper"] > div {
  border-color: var(--line) !important;
  border-radius: 12px;
}

/* ---- badges ---- */
.badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  font-size: .72rem; font-weight: 600; letter-spacing: .3px;
  border: 1px solid var(--line); opacity: .95; margin-right: 6px;
  background: rgba(76,154,255,.08);
}
.badge.green { background: rgba(63,185,80,.15);  border-color: rgba(63,185,80,.45);  color: #7ee2a8; }
.badge.blue  { background: rgba(76,154,255,.15); border-color: rgba(76,154,255,.45); color: #9ecbff; }
.badge.amber { background: rgba(227,179,65,.15); border-color: rgba(227,179,65,.45); color: #f0d489; }
.badge.red   { background: rgba(248,81,73,.14);  border-color: rgba(248,81,73,.45);  color: #ffa8a3; }

/* ---- alerts mais integrados ---- */
[data-testid="stAlert"] { border-radius: 12px; }

/* ---- tabs ---- */
button[role="tab"] { font-weight: 600; }
button[role="tab"][aria-selected="true"] { color: var(--accent) !important; }

/* ---- expanders ---- */
[data-testid="stExpander"] details {
  border: 1px solid var(--line); border-radius: 12px;
  background: var(--surface);
}

/* ---- dataframes ---- */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; }

/* ---- mock exam timer ---- */
.mock-timer {
  font-variant-numeric: tabular-nums; font-weight: 700; font-size: 1.5rem;
  text-align: center; padding: .35rem .8rem; border-radius: 10px;
  border: 1px solid var(--line); background: var(--surface);
}
.mock-timer.low { color: var(--bad); border-color: rgba(248,81,73,.6); }

/* rating buttons fill their column */
div[data-testid="column"] .stButton button { width: 100%; border-radius: 10px; }
.stButton button[kind="primary"] { font-weight: 700; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def badge(text, color=""):
    return f'<span class="badge {color}">{text}</span>'


def card_box(meta_html: str, body_md: str):
    # LaTeX ($...$) não renderiza dentro de blocos HTML; se o corpo tem math,
    # renderiza o markdown fora do div para o KaTeX funcionar.
    if "$" in body_md:
        st.markdown(f'<div class="study-card" style="padding-bottom:.4rem">'
                    f'<div class="meta">{meta_html}</div></div>', unsafe_allow_html=True)
        st.markdown(f"##### {body_md}" if len(body_md) < 200 else body_md)
    else:
        st.markdown(
            f'<div class="study-card"><div class="meta">{meta_html}</div>\n\n{body_md}</div>',
            unsafe_allow_html=True)


def answer_box(md: str, prefix: str = ""):
    """Caixa de resposta com markdown completo (inclui LaTeX $...$)."""
    with st.container(border=True):
        if prefix:
            st.caption(prefix)
        st.markdown(md)


def fmt_pct(x, nd=0):
    return "—" if x is None else f"{100 * x:.{nd}f}%"


def speak_button(text, label="🔊 Listen", height=52):
    """Native pronunciation via the browser's Web Speech API (no audio files,
    works offline). Renders a Listen button + a slow (🐢) button."""
    t = _json.dumps(str(text or ""))
    html = f"""
    <div style="display:flex;gap:8px;font-family:-apple-system,Segoe UI,sans-serif">
      <button id="p" style="cursor:pointer;border:none;border-radius:10px;padding:8px 16px;
        background:#4C9AFF;color:#fff;font-weight:700;font-size:14px">{label}</button>
      <button id="s" title="Slow" style="cursor:pointer;border:1px solid rgba(120,140,170,.4);
        border-radius:10px;padding:8px 12px;background:#1C2330;color:#e3b341;font-size:15px">🐢</button>
    </div>
    <script>
      const _t = {t};
      function _sp(r) {{
        try {{
          speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance(_t);
          u.lang = 'en-US'; u.rate = r;
          const vs = speechSynthesis.getVoices().filter(v => /en[-_]/i.test(v.lang));
          const us = vs.find(v => /en[-_]US/i.test(v.lang)) || vs[0];
          if (us) u.voice = us;
          speechSynthesis.speak(u);
        }} catch (e) {{}}
      }}
      document.getElementById('p').onclick = () => _sp(0.9);
      document.getElementById('s').onclick = () => _sp(0.6);
    </script>
    """
    components.html(html, height=height)


# ============================================================
# Practice session (used by Practice and Error Notebook)
# ============================================================
CONF_OPTS = ["🎯 Sure", "🤔 Guessing"]
CAUSE_OPTS = {"📚 Didn't know it": "content", "👀 Misread the question": "misread",
              "🧮 Calculation slip": "calc", "⏱️ Rushed / time pressure": "time"}


def run_quiz_session(store, user, key: str, mode_label: str):
    """Runs the question session stored in st.session_state[key].

    Answer is logged on "Next" so it can carry confidence + miss cause.
    State: {"cards": [...], "i": 0, "results": [(card, ok, elapsed_ms, conf)],
            "answered": False, "q_start": ts, "start": ts}
    """
    ss = st.session_state
    q = ss.get(key)
    if not q:
        return

    n = len(q["cards"])
    if q["i"] >= n:
        _quiz_summary(q, key)
        return

    c = q["cards"][q["i"]]
    st.progress(q["i"] / n, text=f"Question {q['i'] + 1} of {n}")
    card_box(
        f"{c['topico']} · {c.get('subtopico', '')} · difficulty {c.get('dificuldade', 3)}/5",
        c["enunciado"])

    choice = st.radio("Choices:", c["opcoes"], index=None,
                      key=f"{key}_ch_{q['i']}", label_visibility="collapsed")

    if not q["answered"]:
        conf = st.radio("How confident are you?", CONF_OPTS, horizontal=True,
                        key=f"{key}_cf_{q['i']}")
        if st.button("✅ Submit answer", key=f"{key}_go", type="primary",
                     disabled=choice is None, use_container_width=True):
            elapsed = int((time.time() - q["q_start"]) * 1000)
            ok = c["opcoes"].index(choice) == c["correta"]
            confidence = "sure" if conf == CONF_OPTS[0] else "unsure"
            q["results"].append((c, ok, elapsed, confidence))
            q["answered"] = True
            st.rerun()
    else:
        _, ok, elapsed, confidence = q["results"][-1]
        correta = f"**{chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}**"
        if ok:
            lucky = " (🍀 lucky guess — it stays in the Error notebook)" if confidence == "unsure" else ""
            st.success(f"✅ Correct in {elapsed / 1000:.0f}s{lucky}")
        else:
            st.error("❌ Incorrect.")
        answer_box(f"✅ Answer: {correta}"
                   + (f"\n\n💡 {c['explicacao']}" if c.get("explicacao") else ""))

        cause = None
        if not ok:
            cause_lbl = st.radio("🔬 Why did you miss it? (error autopsy)",
                                 list(CAUSE_OPTS), horizontal=True,
                                 key=f"{key}_ca_{q['i']}")
            cause = CAUSE_OPTS[cause_lbl]

        label = "See results 🏁" if q["i"] == n - 1 else "Next →"
        if st.button(label, key=f"{key}_next", type="primary", use_container_width=True):
            store.log_answer(user, c["id"], c["topico"], ok, mode_label, elapsed,
                             confidence=confidence, cause=cause)
            q["i"] += 1
            q["answered"], q["q_start"] = False, time.time()
            st.rerun()
        if st.button("🚩 Flag this card as wrong/confusing", key=f"{key}_flag_{q['i']}"):
            store.log_flag(user, c["id"], "flagged in quiz")
            st.toast("Card flagged for review ✓")


def _quiz_summary(q, key):
    results = q["results"]
    n = len(results)
    ok_n = sum(1 for _, ok, *_ in results if ok)
    lucky_n = sum(1 for _, ok, _, conf in results if ok and conf == "unsure")
    total_s = sum(r[2] for r in results) / 1000
    pct = ok_n / n if n else 0

    st.subheader("🏁 Session results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", f"{100 * pct:.0f}%", f"{ok_n}/{n}")
    c2.metric("🍀 Lucky guesses", lucky_n)
    c3.metric("Total time", f"{total_s / 60:.1f} min")
    c4.metric("Avg per question", f"{total_s / n:.0f}s" if n else "—")
    if total_s / max(n, 1) > 90:
        st.warning("⏱️ Pace above 90s/question — on the real exam you would have run out of time.")

    by_t = {}
    for c, ok, *_ in results:
        by_t.setdefault(c["topico"], [0, 0])
        by_t[c["topico"]][1] += 1
        by_t[c["topico"]][0] += 1 if ok else 0
    st.write("**By topic:** " + " · ".join(
        f"{t} {o}/{tt}" for t, (o, tt) in sorted(by_t.items())))

    wrongs = [(c, e) for c, ok, e, *_ in results if not ok]
    if wrongs:
        st.subheader(f"❌ Misses ({len(wrongs)}) — already added to the Error Notebook")
        for c, _ in wrongs:
            with st.expander(c["enunciado"][:90]):
                st.markdown(f"✅ {chr(65 + c['correta'])}) {c['opcoes'][c['correta']]}")
                if c.get("explicacao"):
                    st.markdown(c["explicacao"])
    if st.button("🔄 New session", key=f"{key}_restart"):
        del st.session_state[key]
        st.rerun()


def new_quiz_state(cards):
    return {"cards": cards, "i": 0, "results": [], "answered": False,
            "last_ok": None, "q_start": time.time(), "start": time.time()}
