"""Performance: trends, topic accuracy vs target, mocks vs MPS, future review load."""
import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import analytics, ui
from core.content import MPS_BAND, TARGET_ACCURACY
from core.db import cached_cards, get_store
from core.db import user_cards

store = get_store()
user = st.session_state["user"]
cards = user_cards(user)

st.title("📊 Performance")

answers = store.get_answers(user)
df = analytics.answers_df(answers)

if df.empty:
    st.info("Answer questions (Practice / Mock / Review) to see statistics.")
    st.stop()

PLOT_LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                   font_color="#c9d1d9", margin=dict(l=10, r=10, t=40, b=10), height=300)

# ---------------- KPIs ----------------
acc = df["ok"].mean()
last7 = df[df["date"] >= dt.date.today() - dt.timedelta(days=7)]
times = df["elapsed_ms"].dropna()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Overall accuracy", ui.fmt_pct(acc))
c2.metric("Accuracy (7 days)", ui.fmt_pct(last7["ok"].mean() if not last7.empty else None))
c3.metric("Questions answered", len(df))
c4.metric("Avg time/question", f"{times.mean() / 1000:.0f}s" if not times.empty else "—")

tab1, tab2, tab5, tab3, tab4 = st.tabs(
    ["📈 Trend", "🗂️ By topic", "🔬 Diagnosis", "📝 Timed tests", "🔮 Future load"])

# ---------------- trend ----------------
with tab1:
    ds = analytics.daily_series(answers)
    ds["acc7"] = ds["acc"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_bar(x=ds["date"], y=ds["n"], name="Questions/day", opacity=.45, yaxis="y2",
                marker_color="#5B8DEF")
    fig.add_scatter(x=ds["date"], y=100 * ds["acc7"], name="Accuracy (7d avg)",
                    line=dict(color="#2ea043", width=3))
    fig.add_hline(y=100 * TARGET_ACCURACY, line_dash="dot", line_color="#d29922",
                  annotation_text="70% target")
    fig.update_layout(**PLOT_LAYOUT, yaxis=dict(title="% accuracy", range=[0, 100]),
                      yaxis2=dict(overlaying="y", side="right", title="questions", showgrid=False),
                      legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, width="stretch")

# ---------------- by topic ----------------
with tab2:
    tacc = analytics.topic_accuracy(answers)
    tdf = pd.DataFrame([{"Topic": t, "Accuracy": d["acc"], "n": d["n"]}
                        for t, d in tacc.items()]).sort_values("Accuracy")
    fig = px.bar(tdf, x="Accuracy", y="Topic", orientation="h", text="n",
                 color="Accuracy", color_continuous_scale=["#f85149", "#d29922", "#2ea043"],
                 range_color=[0.3, 0.9])
    fig.add_vline(x=TARGET_ACCURACY, line_dash="dot", line_color="#d29922")
    fig.update_traces(texttemplate="%{text} ans.", textposition="outside")
    fig.update_layout(**{**PLOT_LAYOUT, "height": max(300, 40 * len(tdf))},
                      xaxis_tickformat=".0%", coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")
    weak = tdf[(tdf["n"] >= 5) & (tdf["Accuracy"] < 0.6)]["Topic"].tolist()
    if weak:
        st.error("🎯 Study priority: " + ", ".join(weak))

# ---------------- diagnosis (metacognition + autopsy) ----------------
with tab5:
    st.markdown("**Confidence calibration** — knowing what you *don't* know is half the battle.")
    cal = analytics.calibration(answers)
    if cal.empty:
        st.info("Rate your confidence when answering (🎯 Sure / 🤔 Guessing) to unlock "
                "calibration analytics.")
    else:
        st.dataframe(
            cal.drop(columns=["Overconfident"]), hide_index=True, width="stretch",
            column_config={
                "% sure": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
                "Acc. when sure": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
                "Acc. when guessing": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
            })
        over = cal[cal["Overconfident"]]["Topic"].tolist()
        if over:
            st.error("⚠️ **Overconfidence danger zone** (sure but <70% right): " + ", ".join(over) +
                     ". These feel learned but aren't — prioritize them.")
        else:
            st.success("✅ No overconfident topics detected so far.")

    st.divider()
    st.markdown("**Error autopsy** — why you miss questions determines the fix.")
    causes = analytics.cause_breakdown(answers)
    if not causes:
        st.info("Classify your misses (📚/👀/🧮/⏱️) after answering to unlock the autopsy chart.")
    else:
        lbl = {"content": "📚 Didn't know it", "misread": "👀 Misread",
               "calc": "🧮 Calculation slip", "time": "⏱️ Time pressure"}
        cdf = pd.DataFrame([{"Cause": lbl.get(k, k), "Misses": v} for k, v in causes.items()])
        fig = px.bar(cdf, x="Misses", y="Cause", orientation="h", text="Misses")
        fig.update_traces(marker_color="#f85149", textposition="outside")
        fig.update_layout(**{**PLOT_LAYOUT, "height": 220})
        st.plotly_chart(fig, width="stretch")
        fix = {"content": "more cards + concept review on those readings",
               "misread": "slow down: underline what the question asks before the options",
               "calc": "calculator drills; write intermediate steps",
               "time": "practice faster in timed tests"}
        worst = max(causes, key=causes.get)
        st.markdown(f"**Main cause:** {lbl.get(worst, worst)} → **fix:** {fix.get(worst, '')}")

# ---------------- mocks ----------------
with tab3:
    mocks = store.get_mocks(user)
    if not mocks:
        st.info("No timed tests yet — take one in 📝 Timed level test.")
    else:
        mdf = pd.DataFrame([{"ts": str(r["ts"])[:16].replace("T", " "),
                             "pct": float(r["pct"]), "n": r["n"]} for r in reversed(mocks)])
        fig = go.Figure()
        fig.add_hrect(y0=100 * MPS_BAND[0], y1=100 * MPS_BAND[1],
                      fillcolor="rgba(210,153,34,.15)", line_width=0,
                      annotation_text="fluency target (70-80%)")
        fig.add_scatter(x=mdf["ts"], y=mdf["pct"], mode="lines+markers+text",
                        text=[f"{p:.0f}%" for p in mdf["pct"]], textposition="top center",
                        line=dict(color="#5B8DEF", width=3), name="Tests")
        fig.update_layout(**PLOT_LAYOUT, yaxis=dict(title="% accuracy", range=[0, 100]),
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(pd.DataFrame([{
            "Date": str(r["ts"])[:16].replace("T", " "), "Questions": r["n"],
            "Correct": r["correct"], "Score": f"{float(r['pct']):.0f}%",
            "Duration": f"{(r.get('duration_s') or 0) // 60}min"} for r in mocks]),
            hide_index=True, width="stretch")

# ---------------- future load ----------------
with tab4:
    progress = store.get_progress(user)
    fc = analytics.due_forecast(progress, days=14)
    fig = px.bar(fc, x="date", y="due", labels={"date": "", "due": "cards due"})
    fig.update_traces(marker_color="#5B8DEF")
    fig.update_layout(**PLOT_LAYOUT)
    st.plotly_chart(fig, width="stretch")
    st.caption("FSRS review cards coming due per day (overdue counts as today). "
               "Keep the daily queue at zero for the algorithm to work well.")
