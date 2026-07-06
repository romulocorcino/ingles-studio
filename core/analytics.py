"""Métricas derivadas: prontidão ponderada pelos pesos da prova, streak, séries."""
import datetime as dt
import re

import pandas as pd

from . import scheduler
from .content import TOPIC_WEIGHTS, topic_weight

UTC = dt.timezone.utc

# Supabase devolve timestamps com precisão variável de fração de segundo
# (1-6 dígitos); o fromisoformat do Python 3.10 só aceita 3 ou 6. Normaliza p/ 6.
_FRAC = re.compile(r"\.(\d+)")


def _parse_ts(ts):
    if not ts:
        return None
    s = str(ts).replace("Z", "+00:00")
    s = _FRAC.sub(lambda m: "." + (m.group(1) + "000000")[:6], s)
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def answers_df(answers: list) -> pd.DataFrame:
    if not answers:
        return pd.DataFrame(columns=["card_id", "topico", "ok", "mode", "elapsed_ms", "ts", "date"])
    df = pd.DataFrame(answers)
    df["ts"] = df["ts"].apply(_parse_ts)
    df["date"] = df["ts"].apply(lambda t: t.date() if t else None)
    df["ok"] = df["ok"].astype(bool)
    return df


def activity_dates(answers: list, reviews: list) -> set:
    dates = set()
    for r in (answers or []):
        t = _parse_ts(r.get("ts"))
        if t:
            dates.add(t.astimezone().date())
    for r in (reviews or []):
        t = _parse_ts(r.get("ts"))
        if t:
            dates.add(t.astimezone().date())
    return dates


def streak(answers: list, reviews: list) -> int:
    """Dias consecutivos com atividade, terminando hoje ou ontem."""
    dates = activity_dates(answers, reviews)
    if not dates:
        return 0
    today = dt.date.today()
    day = today if today in dates else today - dt.timedelta(days=1)
    if day not in dates:
        return 0
    n = 0
    while day in dates:
        n += 1
        day -= dt.timedelta(days=1)
    return n


def topic_accuracy(answers: list, last_n: int = 100) -> dict:
    """Acurácia por tópico considerando as últimas `last_n` respostas de cada tópico."""
    df = answers_df(answers)
    out = {}
    if df.empty:
        return out
    for t, g in df.groupby("topico"):
        g = g.sort_values("ts").tail(last_n)
        out[t] = {"acc": g["ok"].mean(), "n": len(g)}
    return out


def topic_srs_maturity(cards: list, progress: dict) -> dict:
    """Fração dos cards de cada tópico que estão 'maduros' no FSRS."""
    out = {}
    by_topic = {}
    for c in cards:
        by_topic.setdefault(c["topico"], []).append(c)
    for t, cs in by_topic.items():
        mature = sum(1 for c in cs if scheduler.is_mature(progress.get(c["id"])))
        started = sum(1 for c in cs if progress.get(c["id"]))
        out[t] = {"mature_frac": mature / len(cs), "started": started, "total": len(cs)}
    return out


def readiness(cards: list, progress: dict, answers: list) -> dict:
    """Prontidão 0..1 por tópico e geral, ponderada pelos pesos oficiais da prova.

    Por tópico: 50% maturidade FSRS + 50% acurácia em questões (se houver dados).
    Tópicos sem nenhum card contam 0 (lacuna de cobertura).
    """
    acc = topic_accuracy(answers)
    srs = topic_srs_maturity(cards, progress)
    per_topic, total = {}, 0.0
    for t in TOPIC_WEIGHTS:
        w = topic_weight(t)
        m = srs.get(t, {}).get("mature_frac", 0.0)
        a = acc.get(t, {}).get("acc")
        score = (0.5 * m + 0.5 * a) if a is not None else 0.7 * m
        per_topic[t] = {"score": score, "weight": w,
                        "maturity": m, "accuracy": a,
                        "cards": srs.get(t, {}).get("total", 0),
                        "answered": acc.get(t, {}).get("n", 0)}
        total += w * score
    return {"overall": total, "topics": per_topic}


def due_forecast(progress: dict, days: int = 14) -> pd.DataFrame:
    """Cards de revisão vencendo por dia nos próximos `days` dias."""
    today = dt.date.today()
    counts = {today + dt.timedelta(days=i): 0 for i in range(days)}
    backlog = 0
    for p in progress.values():
        if p.get("suspended") or not p.get("due"):
            continue
        d = _parse_ts(p["due"]).astimezone().date()
        if d < today:
            backlog += 1
        elif d in counts:
            counts[d] += 1
    counts[today] += backlog  # atrasados entram em "hoje"
    return pd.DataFrame({"date": list(counts.keys()), "due": list(counts.values())})


def daily_series(answers: list, weeks: int = 6) -> pd.DataFrame:
    """Volume e acurácia por dia nas últimas `weeks` semanas."""
    df = answers_df(answers)
    start = dt.date.today() - dt.timedelta(weeks=weeks)
    idx = pd.date_range(start, dt.date.today(), freq="D").date
    if df.empty:
        return pd.DataFrame({"date": idx, "n": 0, "acc": None})
    g = df[df["date"] >= start].groupby("date").agg(n=("ok", "size"), acc=("ok", "mean"))
    g = g.reindex(idx)
    g["n"] = g["n"].fillna(0).astype(int)
    return g.reset_index().rename(columns={"index": "date"})


def error_notebook(cards: list, answers: list) -> list:
    """Questions pending re-drill: last answer wrong, OR last answer correct
    but flagged as a guess (🍀 lucky — you don't actually know it yet).

    Each entry carries `misses` (total historical misses); 2+ misses marks the
    question as HARD — those are drilled first, then lucky guesses.
    """
    last, misses = {}, {}
    for a in answers:
        cid = a.get("card_id")
        if not cid:
            continue
        last[cid] = a
        if not a["ok"]:
            misses[cid] = misses.get(cid, 0) + 1
    by_id = {c["id"]: c for c in cards}
    out = []
    for cid, a in last.items():
        lucky = bool(a["ok"] and a.get("confidence") == "unsure")
        if a["ok"] and not lucky:
            continue
        c = by_id.get(cid)
        if c and c.get("tipo") == "questao":
            n_miss = misses.get(cid, 0)
            out.append({"card": c, "when": a.get("ts"), "misses": max(n_miss, 0),
                        "hard": n_miss >= 2, "lucky": lucky})
    # recent first; then (stable) hard first, misses next, lucky last
    out.sort(key=lambda x: str(x["when"] or ""), reverse=True)
    out.sort(key=lambda x: (0 if x["hard"] else (2 if x["lucky"] else 1), -x["misses"]))
    return out


def most_missed(cards: list, answers: list, top_n: int = 25) -> list:
    """Cards you miss the most, ranked. Combines total miss count with recent
    miss rate so a card you keep failing rises to the top."""
    by_id = {c["id"]: c for c in cards}
    stats = {}
    for a in answers:
        cid = a.get("card_id")
        if not cid or cid not in by_id:
            continue
        s = stats.setdefault(cid, {"misses": 0, "attempts": 0, "last_ts": ""})
        s["attempts"] += 1
        if not a["ok"]:
            s["misses"] += 1
        s["last_ts"] = max(s["last_ts"], str(a.get("ts") or ""))
    out = []
    for cid, s in stats.items():
        if s["misses"] == 0:
            continue
        miss_rate = s["misses"] / s["attempts"]
        out.append({"card": by_id[cid], "misses": s["misses"], "attempts": s["attempts"],
                    "miss_rate": miss_rate, "score": s["misses"] + miss_rate})
    out.sort(key=lambda x: (-x["misses"], -x["miss_rate"]))
    return out[:top_n]


def weakest_topics(answers: list, min_n: int = 3) -> list:
    """Topics ranked by miss count (with accuracy), driven by actual errors."""
    df = answers_df(answers)
    if df.empty:
        return []
    rows = []
    for t, g in df.groupby("topico"):
        miss = int((~g["ok"]).sum())
        if miss == 0 or len(g) < min_n:
            continue
        rows.append({"topic": t, "misses": miss, "attempts": len(g), "acc": g["ok"].mean()})
    rows.sort(key=lambda x: (-x["misses"], x["acc"]))
    return rows


def calibration(answers: list, min_n: int = 5) -> pd.DataFrame:
    """Confidence calibration by topic: accuracy when 'sure' vs when 'guessing'.

    Overconfident topics (sure but wrong) are the danger zone on exam day.
    """
    df = answers_df(answers)
    if df.empty or "confidence" not in df.columns:
        return pd.DataFrame()
    df = df[df["confidence"].notna()]
    if df.empty:
        return pd.DataFrame()
    rows = []
    for t, g in df.groupby("topico"):
        sure = g[g["confidence"] == "sure"]
        guess = g[g["confidence"] == "unsure"]
        if len(g) < min_n:
            continue
        rows.append({
            "Topic": t, "Answers": len(g),
            "% sure": len(sure) / len(g),
            "Acc. when sure": sure["ok"].mean() if len(sure) else None,
            "Acc. when guessing": guess["ok"].mean() if len(guess) else None,
            "Overconfident": bool(len(sure) >= min_n and sure["ok"].mean() < 0.70),
        })
    return pd.DataFrame(rows)


def cause_breakdown(answers: list) -> dict:
    """Distribution of miss causes from the error autopsy."""
    df = answers_df(answers)
    if df.empty or "cause" not in df.columns:
        return {}
    df = df[(~df["ok"]) & df["cause"].notna()]
    return df["cause"].value_counts().to_dict()
