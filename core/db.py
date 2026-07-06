"""Camada de dados com dois backends intercambiáveis:

- SupabaseStore: produção (Streamlit Cloud, progresso sincronizado entre aparelhos)
- LocalStore:    SQLite local — roda sem nenhuma configuração (testes/offline)

O backend é escolhido automaticamente: com SUPABASE_URL/KEY nos secrets usa
Supabase; sem eles, usa `local_data.db` ao lado do app.
"""
import datetime as dt
import json
import os
import sqlite3

import streamlit as st

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DB = os.path.join(APP_DIR, "local_data.db")
UTC = dt.timezone.utc

PROGRESS_FIELDS = ["state", "step", "stability", "difficulty", "reps", "lapses",
                   "due", "last", "suspended"]


def _secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        return None


# ============================================================ Supabase
class SupabaseStore:
    mode = "supabase"

    def __init__(self, url, key):
        from supabase import create_client
        self.client = create_client(url, key)
        # valida conectividade/credenciais logo de cara; se falhar (DNS, chave
        # inválida, projeto fora do ar), get_store() cai para o modo local.
        self.client.table("cards").select("id").limit(1).execute()

    # ---- cards
    def get_cards(self):
        return self.client.table("cards").select("*").execute().data or []

    def upsert_cards(self, cards):
        for i in range(0, len(cards), 100):
            self.client.table("cards").upsert(cards[i:i + 100]).execute()

    # ---- progress
    def get_progress(self, user):
        rows = self.client.table("progress").select("*").eq("user_id", user).execute().data or []
        return {r["card_id"]: r for r in rows}

    def upsert_progress(self, user, card_id, state):
        row = {"user_id": user, "card_id": card_id}
        row.update({k: state.get(k) for k in PROGRESS_FIELDS})
        self.client.table("progress").upsert(row, on_conflict="user_id,card_id").execute()

    def delete_progress(self, user):
        self.client.table("progress").delete().eq("user_id", user).execute()

    # ---- reviews (log FSRS)
    def log_review(self, user, card_id, rating, prev_state, new_state, elapsed_ms):
        self.client.table("reviews").insert({
            "user_id": user, "card_id": card_id, "rating": rating,
            "prev_state": prev_state, "state": new_state.get("state"),
            "stability": new_state.get("stability"), "difficulty": new_state.get("difficulty"),
            "elapsed_ms": elapsed_ms}).execute()

    def get_reviews(self, user):
        return self.client.table("reviews").select("card_id,rating,prev_state,state,ts") \
            .eq("user_id", user).execute().data or []

    def delete_reviews(self, user):
        self.client.table("reviews").delete().eq("user_id", user).execute()

    # ---- answers
    def log_answer(self, user, card_id, topico, ok, mode_, elapsed_ms,
                   confidence=None, cause=None):
        self.client.table("answers").insert({
            "user_id": user, "card_id": card_id, "topico": topico,
            "ok": bool(ok), "mode": mode_, "elapsed_ms": elapsed_ms,
            "confidence": confidence, "cause": cause}).execute()

    def get_answers(self, user):
        return self.client.table("answers") \
            .select("card_id,topico,ok,mode,elapsed_ms,confidence,cause,ts") \
            .eq("user_id", user).order("ts").execute().data or []

    def delete_answers(self, user):
        self.client.table("answers").delete().eq("user_id", user).execute()

    # ---- mocks
    def log_mock(self, user, payload):
        row = {"user_id": user}
        row.update(payload)
        self.client.table("mocks").insert(row).execute()

    def get_mocks(self, user):
        return self.client.table("mocks").select("*").eq("user_id", user) \
            .order("ts", desc=True).limit(50).execute().data or []

    def delete_mocks(self, user):
        self.client.table("mocks").delete().eq("user_id", user).execute()

    # ---- settings
    def get_settings(self, user):
        rows = self.client.table("settings").select("*").eq("user_id", user).execute().data
        return rows[0] if rows else {}

    def save_settings(self, user, settings):
        row = {"user_id": user}
        row.update(settings)
        self.client.table("settings").upsert(row, on_conflict="user_id").execute()

    # ---- flags (suspect/confusing cards). Resilient: never crash the app if
    # the flags table is missing (falls back to no-op / empty).
    def log_flag(self, user, card_id, reason):
        try:
            self.client.table("flags").insert(
                {"user_id": user, "card_id": card_id, "reason": reason}).execute()
        except Exception:
            pass

    def get_flags(self, user):
        try:
            return self.client.table("flags").select("card_id,reason,ts") \
                .eq("user_id", user).order("ts", desc=True).execute().data or []
        except Exception:
            return []

    def delete_flag(self, user, card_id):
        try:
            self.client.table("flags").delete().eq("user_id", user).eq("card_id", card_id).execute()
        except Exception:
            pass

    # ---- auth: contas, solicitações de acesso, auditoria
    def get_app_user(self, email):
        r = self.client.table("app_users").select("*").eq("email", email).execute().data
        return r[0] if r else None

    def upsert_app_user(self, row):
        self.client.table("app_users").upsert(row, on_conflict="email").execute()

    def delete_app_user(self, email):
        self.client.table("app_users").delete().eq("email", email).execute()

    def list_app_users(self):
        return self.client.table("app_users").select(
            "email,name,role,level,active,must_change_pw,created_at").order("created_at").execute().data or []

    def add_access_request(self, row):
        self.client.table("access_requests").insert(row).execute()

    def list_access_requests(self, status=None):
        q = self.client.table("access_requests").select("*").order("ts", desc=True)
        if status:
            q = q.eq("status", status)
        return q.execute().data or []

    def update_access_request(self, req_id, status):
        self.client.table("access_requests").update({"status": status}).eq("id", req_id).execute()

    def log_audit(self, actor, action, target=""):
        try:
            self.client.table("audit_log").insert({"actor": actor, "action": action, "target": target}).execute()
        except Exception:
            pass

    def list_audit(self, limit=200):
        try:
            return self.client.table("audit_log").select("*").order("ts", desc=True).limit(limit).execute().data or []
        except Exception:
            return []


# ============================================================ SQLite local
_LOCAL_SCHEMA = """
create table if not exists cards (
  id text primary key, tipo text, topico text, subtopico text,
  dificuldade int, tags text, fonte text, enunciado text, opcoes text,
  correta int, frente text, verso text, explicacao text, imagem text);
create table if not exists progress (
  user_id text, card_id text, state text, step int, stability real,
  difficulty real, reps int, lapses int, due text, last text,
  suspended int default 0, primary key (user_id, card_id));
create table if not exists reviews (
  id integer primary key autoincrement, user_id text, card_id text, rating text,
  prev_state text, state text, stability real, difficulty real,
  elapsed_ms int, ts text default (datetime('now')));
create table if not exists flags (
  id integer primary key autoincrement, user_id text, card_id text, reason text,
  ts text default (datetime('now')));
create table if not exists answers (
  id integer primary key autoincrement, user_id text, card_id text, topico text,
  ok int, mode text, elapsed_ms int, confidence text, cause text,
  ts text default (datetime('now')));
create table if not exists mocks (
  id integer primary key autoincrement, user_id text, n int, correct int,
  pct real, duration_s int, detail text, ts text default (datetime('now')));
create table if not exists settings (
  user_id text primary key, exam_date text, retention real, daily_new int,
  daily_goal int, updated_at text);
create table if not exists app_users (
  email text primary key, name text, password_hash text, role text default 'user',
  level text default '', active int default 1, must_change_pw int default 0,
  failed_attempts int default 0, locked_until text, created_at text);
create table if not exists access_requests (
  id integer primary key autoincrement, email text, name text, message text,
  status text default 'pending', ts text default (datetime('now')));
create table if not exists audit_log (
  id integer primary key autoincrement, actor text, action text, target text,
  ts text default (datetime('now')));
"""

_CARD_COLS = ["id", "tipo", "topico", "subtopico", "dificuldade", "tags", "fonte",
              "enunciado", "opcoes", "correta", "frente", "verso", "explicacao", "imagem"]


class LocalStore:
    mode = "local"

    def __init__(self, path=LOCAL_DB):
        self.path = path
        with self._conn() as c:
            c.executescript(_LOCAL_SCHEMA)
            # migração leve: bases antigas sem colunas novas
            for col in ("confidence", "cause"):
                try:
                    c.execute(f"alter table answers add column {col} text")
                except sqlite3.OperationalError:
                    pass
            try:
                c.execute("alter table cards add column imagem text")
            except sqlite3.OperationalError:
                pass
            c.execute("create table if not exists flags (id integer primary key autoincrement, "
                      "user_id text, card_id text, reason text, ts text default (datetime('now')))")

    def _conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def _ts():
        return dt.datetime.now(UTC).isoformat()

    # ---- cards
    def get_cards(self):
        with self._conn() as c:
            rows = [dict(r) for r in c.execute("select * from cards").fetchall()]
        for r in rows:
            r["tags"] = json.loads(r["tags"]) if r.get("tags") else []
            r["opcoes"] = json.loads(r["opcoes"]) if r.get("opcoes") else None
        return rows

    def upsert_cards(self, cards):
        with self._conn() as c:
            for card in cards:
                row = {k: card.get(k) for k in _CARD_COLS}
                row["tags"] = json.dumps(row.get("tags") or [], ensure_ascii=False)
                row["opcoes"] = json.dumps(row["opcoes"], ensure_ascii=False) if row.get("opcoes") is not None else None
                c.execute(
                    f"insert or replace into cards ({','.join(_CARD_COLS)}) "
                    f"values ({','.join('?' * len(_CARD_COLS))})",
                    [row[k] for k in _CARD_COLS])

    # ---- progress
    def get_progress(self, user):
        with self._conn() as c:
            rows = c.execute("select * from progress where user_id=?", (user,)).fetchall()
        out = {}
        for r in rows:
            d = dict(r)
            d["suspended"] = bool(d.get("suspended"))
            out[d["card_id"]] = d
        return out

    def upsert_progress(self, user, card_id, state):
        vals = [state.get(k) for k in PROGRESS_FIELDS]
        vals[PROGRESS_FIELDS.index("suspended")] = 1 if state.get("suspended") else 0
        with self._conn() as c:
            c.execute(
                f"insert or replace into progress (user_id, card_id, {','.join(PROGRESS_FIELDS)}) "
                f"values (?,?,{','.join('?' * len(PROGRESS_FIELDS))})",
                [user, card_id] + vals)

    def delete_progress(self, user):
        with self._conn() as c:
            c.execute("delete from progress where user_id=?", (user,))

    # ---- reviews
    def log_review(self, user, card_id, rating, prev_state, new_state, elapsed_ms):
        with self._conn() as c:
            c.execute(
                "insert into reviews (user_id,card_id,rating,prev_state,state,stability,difficulty,elapsed_ms,ts) "
                "values (?,?,?,?,?,?,?,?,?)",
                (user, card_id, rating, prev_state, new_state.get("state"),
                 new_state.get("stability"), new_state.get("difficulty"), elapsed_ms, self._ts()))

    def get_reviews(self, user):
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "select card_id,rating,prev_state,state,ts from reviews where user_id=? order by ts",
                (user,)).fetchall()]

    def delete_reviews(self, user):
        with self._conn() as c:
            c.execute("delete from reviews where user_id=?", (user,))

    # ---- flags
    def log_flag(self, user, card_id, reason):
        with self._conn() as c:
            c.execute("insert into flags (user_id,card_id,reason,ts) values (?,?,?,?)",
                      (user, card_id, reason, self._ts()))

    def get_flags(self, user):
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "select card_id,reason,ts from flags where user_id=? order by ts desc",
                (user,)).fetchall()]

    def delete_flag(self, user, card_id):
        with self._conn() as c:
            c.execute("delete from flags where user_id=? and card_id=?", (user, card_id))

    # ---- answers
    def log_answer(self, user, card_id, topico, ok, mode_, elapsed_ms,
                   confidence=None, cause=None):
        with self._conn() as c:
            c.execute(
                "insert into answers (user_id,card_id,topico,ok,mode,elapsed_ms,confidence,cause,ts) "
                "values (?,?,?,?,?,?,?,?,?)",
                (user, card_id, topico, 1 if ok else 0, mode_, elapsed_ms,
                 confidence, cause, self._ts()))

    def get_answers(self, user):
        with self._conn() as c:
            rows = [dict(r) for r in c.execute(
                "select card_id,topico,ok,mode,elapsed_ms,confidence,cause,ts "
                "from answers where user_id=? order by ts",
                (user,)).fetchall()]
        for r in rows:
            r["ok"] = bool(r["ok"])
        return rows

    def delete_answers(self, user):
        with self._conn() as c:
            c.execute("delete from answers where user_id=?", (user,))

    # ---- mocks
    def log_mock(self, user, payload):
        with self._conn() as c:
            c.execute(
                "insert into mocks (user_id,n,correct,pct,duration_s,detail,ts) values (?,?,?,?,?,?,?)",
                (user, payload.get("n"), payload.get("correct"), payload.get("pct"),
                 payload.get("duration_s"), json.dumps(payload.get("detail") or {}, ensure_ascii=False),
                 self._ts()))

    def get_mocks(self, user):
        with self._conn() as c:
            rows = [dict(r) for r in c.execute(
                "select * from mocks where user_id=? order by ts desc limit 50", (user,)).fetchall()]
        for r in rows:
            r["detail"] = json.loads(r["detail"]) if r.get("detail") else {}
        return rows

    def delete_mocks(self, user):
        with self._conn() as c:
            c.execute("delete from mocks where user_id=?", (user,))

    # ---- settings
    def get_settings(self, user):
        with self._conn() as c:
            r = c.execute("select * from settings where user_id=?", (user,)).fetchone()
        return dict(r) if r else {}

    def save_settings(self, user, settings):
        keys = ["exam_date", "retention", "daily_new", "daily_goal"]
        with self._conn() as c:
            c.execute(
                "insert or replace into settings (user_id,exam_date,retention,daily_new,daily_goal,updated_at) "
                "values (?,?,?,?,?,?)",
                [user] + [settings.get(k) for k in keys] + [self._ts()])

    # ---- auth
    def get_app_user(self, email):
        with self._conn() as c:
            r = c.execute("select * from app_users where email=?", (email,)).fetchone()
        if not r:
            return None
        d = dict(r)
        d["active"] = bool(d.get("active"))
        d["must_change_pw"] = bool(d.get("must_change_pw"))
        return d

    def upsert_app_user(self, row):
        cols = ["email", "name", "password_hash", "role", "level", "active",
                "must_change_pw", "failed_attempts", "locked_until", "created_at"]
        r = {k: row.get(k) for k in cols}
        r["active"] = 1 if r.get("active", True) else 0
        r["must_change_pw"] = 1 if r.get("must_change_pw") else 0
        with self._conn() as c:
            c.execute(
                f"insert or replace into app_users ({','.join(cols)}) values ({','.join('?' * len(cols))})",
                [r[k] for k in cols])

    def delete_app_user(self, email):
        with self._conn() as c:
            c.execute("delete from app_users where email=?", (email,))

    def list_app_users(self):
        with self._conn() as c:
            rows = [dict(x) for x in c.execute(
                "select email,name,role,level,active,must_change_pw,created_at "
                "from app_users order by created_at").fetchall()]
        for d in rows:
            d["active"] = bool(d.get("active"))
            d["must_change_pw"] = bool(d.get("must_change_pw"))
        return rows

    def add_access_request(self, row):
        with self._conn() as c:
            c.execute("insert into access_requests (email,name,message,status,ts) values (?,?,?,?,?)",
                      (row.get("email"), row.get("name"), row.get("message"),
                       row.get("status", "pending"), self._ts()))

    def list_access_requests(self, status=None):
        with self._conn() as c:
            if status:
                rows = c.execute("select * from access_requests where status=? order by ts desc",
                                 (status,)).fetchall()
            else:
                rows = c.execute("select * from access_requests order by ts desc").fetchall()
        return [dict(x) for x in rows]

    def update_access_request(self, req_id, status):
        with self._conn() as c:
            c.execute("update access_requests set status=? where id=?", (status, req_id))

    def log_audit(self, actor, action, target=""):
        with self._conn() as c:
            c.execute("insert into audit_log (actor,action,target,ts) values (?,?,?,?)",
                      (actor, action, target, self._ts()))

    def list_audit(self, limit=200):
        with self._conn() as c:
            return [dict(x) for x in c.execute(
                "select * from audit_log order by ts desc limit ?", (limit,)).fetchall()]


# ============================================================ factory
@st.cache_resource
def get_store():
    _store_schema_version = "2"  # bump quando mudar métodos das stores (invalida este cache_resource)
    url, key = _secret("SUPABASE_URL"), _secret("SUPABASE_KEY")
    if url and key:
        try:
            return SupabaseStore(url, key)
        except Exception as e:
            st.warning(f"Supabase indisponível ({e}) — usando modo local.")
    return LocalStore()


@st.cache_data(ttl=120)
def cached_cards():
    return get_store().get_cards()


def clear_card_cache():
    cached_cards.clear()
