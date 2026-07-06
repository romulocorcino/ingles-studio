"""FSRS-4.5 — algoritmo de repetição espaçada usado pelo Anki moderno.

Modela cada card com dois estados de memória:
  - stability (S): dias para a retenção cair à retenção-alvo
  - difficulty (D): 1..10, quão difícil o card é para VOCÊ

Ratings: 1=again (errei), 2=hard, 3=good, 4=easy.
Estados do card: new -> learning -> review (-> relearning ao errar).
"""
import datetime as dt
import math
import random
import re

W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
     1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]
DECAY = -0.5
FACTOR = 19 / 81
MAX_INTERVAL = 365            # dias
LEARNING_STEPS_MIN = [1, 10]  # minutos (cards novos)
RELEARNING_STEPS_MIN = [10]   # minutos (após lapso)

RATINGS = {"again": 1, "hard": 2, "good": 3, "easy": 4}
UTC = dt.timezone.utc
_FRAC = re.compile(r"\.(\d+)")


def _now():
    return dt.datetime.now(UTC)


def _parse(ts):
    """Parse ISO timestamp tolerating Supabase's variable fractional-second
    precision (Python 3.10 fromisoformat only accepts 3 or 6 digits)."""
    s = _FRAC.sub(lambda m: "." + (m.group(1) + "000000")[:6], str(ts).replace("Z", "+00:00"))
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def retrievability(elapsed_days: float, stability: float) -> float:
    if stability <= 0:
        return 0.0
    return (1 + FACTOR * elapsed_days / stability) ** DECAY


def interval_for(stability: float, retention: float) -> float:
    """Intervalo (dias) para a retenção cair até `retention`."""
    return stability / FACTOR * (retention ** (1 / DECAY) - 1)


def _init_difficulty(g: int) -> float:
    d = W[4] - math.exp(W[5] * (g - 1)) + 1
    return min(10.0, max(1.0, d))


def _init_stability(g: int) -> float:
    return max(0.1, W[g - 1])


def _next_difficulty(d: float, g: int) -> float:
    dn = d - W[6] * (g - 3)
    dn = W[7] * _init_difficulty(4) + (1 - W[7]) * dn  # mean reversion
    return min(10.0, max(1.0, dn))


def _stability_success(d, s, r, g):
    hard_penalty = W[15] if g == 2 else 1.0
    easy_bonus = W[16] if g == 4 else 1.0
    inc = (math.exp(W[8]) * (11 - d) * s ** (-W[9]) *
           (math.exp(W[10] * (1 - r)) - 1) * hard_penalty * easy_bonus)
    return s * (inc + 1)


def _stability_fail(d, s, r):
    sf = (W[11] * d ** (-W[12]) * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r)))
    return min(sf, s)


def default_state() -> dict:
    return {"state": "new", "step": 0, "stability": 0.0, "difficulty": 0.0,
            "reps": 0, "lapses": 0, "due": None, "last": None, "suspended": False}


def _fuzz(days: float) -> float:
    if days < 2.5:
        return days
    return days * random.uniform(0.95, 1.05)


def _schedule_days(state: dict, retention: float, fuzz: bool = True) -> float:
    ivl = interval_for(state["stability"], retention)
    if fuzz:
        ivl = _fuzz(ivl)
    return min(MAX_INTERVAL, max(1.0, round(ivl)))


def review(prev: dict | None, rating: str, retention: float = 0.9,
           now: dt.datetime | None = None, fuzz: bool = True) -> dict:
    """Aplica um rating e retorna o novo estado do card."""
    now = now or _now()
    g = RATINGS[rating]
    s = dict(prev) if prev else default_state()
    s.setdefault("step", 0); s.setdefault("lapses", 0)

    elapsed = 0.0
    if s.get("last"):
        elapsed = max(0.0, (now - _parse(s["last"])).total_seconds() / 86400)

    if s["state"] == "new":
        s["stability"] = _init_stability(g)
        s["difficulty"] = _init_difficulty(g)
        if g == 4:  # easy: gradua direto
            s["state"] = "review"
            s["due"] = (now + dt.timedelta(days=_schedule_days(s, retention, fuzz))).isoformat()
        elif g == 3 and len(LEARNING_STEPS_MIN) <= 1:
            s["state"] = "review"
            s["due"] = (now + dt.timedelta(days=_schedule_days(s, retention, fuzz))).isoformat()
        else:
            s["state"] = "learning"
            s["step"] = 1 if g == 3 else 0
            minutes = LEARNING_STEPS_MIN[min(s["step"], len(LEARNING_STEPS_MIN) - 1)]
            if g == 2:
                minutes = max(1, round(minutes * 1.5))
            s["due"] = (now + dt.timedelta(minutes=minutes)).isoformat()

    elif s["state"] in ("learning", "relearning"):
        steps = LEARNING_STEPS_MIN if s["state"] == "learning" else RELEARNING_STEPS_MIN
        r = retrievability(elapsed, s["stability"]) if s["stability"] else 0.9
        if g == 1:
            s["step"] = 0
            s["due"] = (now + dt.timedelta(minutes=steps[0])).isoformat()
        elif g == 2:
            minutes = steps[min(s["step"], len(steps) - 1)]
            s["due"] = (now + dt.timedelta(minutes=max(1, round(minutes * 1.5)))).isoformat()
        else:  # good/easy
            nxt = s["step"] + 1
            if g == 4 or nxt >= len(steps):  # gradua
                s["state"] = "review"
                s["step"] = 0
                s["stability"] = _stability_success(s["difficulty"], max(s["stability"], 0.1), r, g)
                s["difficulty"] = _next_difficulty(s["difficulty"], g)
                s["due"] = (now + dt.timedelta(days=_schedule_days(s, retention, fuzz))).isoformat()
            else:
                s["step"] = nxt
                s["due"] = (now + dt.timedelta(minutes=steps[min(nxt, len(steps) - 1)])).isoformat()

    else:  # review
        r = retrievability(elapsed, s["stability"]) if s["stability"] else 0.9
        if g == 1:
            s["lapses"] += 1
            s["stability"] = _stability_fail(s["difficulty"], s["stability"], r)
            s["difficulty"] = _next_difficulty(s["difficulty"], g)
            s["state"] = "relearning"
            s["step"] = 0
            s["due"] = (now + dt.timedelta(minutes=RELEARNING_STEPS_MIN[0])).isoformat()
        else:
            s["stability"] = _stability_success(s["difficulty"], s["stability"], r, g)
            s["difficulty"] = _next_difficulty(s["difficulty"], g)
            s["due"] = (now + dt.timedelta(days=_schedule_days(s, retention, fuzz))).isoformat()

    s["reps"] = (s.get("reps") or 0) + 1
    s["last"] = now.isoformat()
    return s


def preview_intervals(prev: dict | None, retention: float = 0.9) -> dict:
    """Intervalo previsto (texto) para cada rating — mostrado nos botões, como no Anki."""
    now = _now()
    out = {}
    for rt in RATINGS:
        nxt = review(prev, rt, retention, now=now, fuzz=False)
        delta = _parse(nxt["due"]) - now
        mins = delta.total_seconds() / 60
        if mins < 60:
            out[rt] = f"{max(1, round(mins))}m"
        elif mins < 60 * 36:
            out[rt] = f"{round(mins / 60)}h" if mins < 60 * 24 else "1d"
        else:
            days = delta.days
            out[rt] = f"{days}d" if days < 30 else f"{days / 30:.1f}mês"
    return out


def is_due(prog: dict | None, now: dt.datetime | None = None) -> bool:
    if not prog or not prog.get("due"):
        return True  # card novo
    if prog.get("suspended"):
        return False
    now = now or _now()
    return _parse(prog["due"]) <= now


def is_mature(prog: dict | None) -> bool:
    """Card 'dominado': em review com estabilidade >= 21 dias."""
    return bool(prog and prog.get("state") == "review" and (prog.get("stability") or 0) >= 21)
