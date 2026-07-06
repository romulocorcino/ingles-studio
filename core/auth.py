"""Autenticação e segurança do English Studio.

Modelo: o app roda no servidor (Streamlit), então a chave do Supabase e os hashes
nunca vão para o navegador. Senhas com PBKDF2-HMAC-SHA256 (salt por usuário, 200k
iterações — sem dependências externas). Bloqueio após tentativas erradas, papéis
(admin/user), solicitação de acesso e log de auditoria.
"""
import base64
import datetime as dt
import hashlib
import hmac
import re
import secrets as _secrets

ADMIN_EMAIL = "romullor10@gmail.com"
MIN_PW = 8
MAX_FAILS = 5
LOCK_MINUTES = 15
PBKDF2_ITERS = 200_000
UTC = dt.timezone.utc
_FRAC = re.compile(r"\.(\d+)")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------- helpers ----------------
def normalize_email(e):
    return (e or "").strip().lower()


def valid_email(e):
    return bool(_EMAIL_RE.match(normalize_email(e)))


def _now():
    return dt.datetime.now(UTC)


def _parse(ts):
    if not ts:
        return None
    s = _FRAC.sub(lambda m: "." + (m.group(1) + "000000")[:6], str(ts).replace("Z", "+00:00"))
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def temp_password(n=10):
    return _secrets.token_urlsafe(n)[:n]


# ---------------- password hashing (PBKDF2) ----------------
def hash_password(pw):
    salt = _secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, PBKDF2_ITERS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERS, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def verify_password(pw, stored):
    try:
        algo, iters, salt_b64, hash_b64 = (stored or "").split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, int(iters))
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def password_problem(pw):
    if len(pw or "") < MIN_PW:
        return f"A senha precisa de pelo menos {MIN_PW} caracteres."
    if not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return "A senha deve conter letras e números."
    return None


# ---------------- roles ----------------
def is_admin(user):
    if not user:
        return False
    return user.get("role") == "admin" or normalize_email(user.get("email")) == ADMIN_EMAIL


# ---------------- auth flows ----------------
def authenticate(store, email, pw):
    """Retorna (user_dict, None) em sucesso ou (None, mensagem_erro)."""
    email = normalize_email(email)
    u = store.get_app_user(email)
    generic = "E-mail ou senha inválidos."
    if not u or not u.get("active", True):
        return None, generic
    locked = _parse(u.get("locked_until"))
    if locked and locked > _now():
        mins = max(1, int((locked - _now()).total_seconds() // 60))
        return None, f"Conta bloqueada por muitas tentativas. Tente em ~{mins} min."
    if verify_password(pw, u.get("password_hash", "")):
        store.upsert_app_user({**u, "failed_attempts": 0, "locked_until": None})
        store.log_audit(email, "login_success", "")
        return u, None
    # falha: incrementa e bloqueia se necessário
    fa = (u.get("failed_attempts") or 0) + 1
    upd = {**u, "failed_attempts": fa, "locked_until": None}
    if fa >= MAX_FAILS:
        upd["failed_attempts"] = 0
        upd["locked_until"] = (_now() + dt.timedelta(minutes=LOCK_MINUTES)).isoformat()
    store.upsert_app_user(upd)
    store.log_audit(email, "login_fail", "")
    return None, generic


def create_user(store, email, name, pw, role="user", level="", must_change=True):
    email = normalize_email(email)
    if not valid_email(email):
        return "E-mail inválido."
    if store.get_app_user(email):
        return "Já existe uma conta com esse e-mail."
    prob = password_problem(pw)
    if prob:
        return prob
    store.upsert_app_user({
        "email": email, "name": (name or "").strip() or email.split("@")[0],
        "password_hash": hash_password(pw), "role": role, "level": level,
        "active": True, "must_change_pw": must_change,
        "failed_attempts": 0, "locked_until": None, "created_at": _now().isoformat()})
    return None


def change_password(store, email, old_pw, new_pw):
    email = normalize_email(email)
    u = store.get_app_user(email)
    if not u or not verify_password(old_pw, u.get("password_hash", "")):
        return "Senha atual incorreta."
    prob = password_problem(new_pw)
    if prob:
        return prob
    store.upsert_app_user({**u, "password_hash": hash_password(new_pw), "must_change_pw": False})
    store.log_audit(email, "password_change", "")
    return None


def set_password(store, email, new_pw, must_change=False):
    """Define senha sem checar a antiga (troca forçada ou reset pelo admin)."""
    email = normalize_email(email)
    u = store.get_app_user(email)
    if not u:
        return "Usuário não encontrado."
    prob = password_problem(new_pw)
    if prob:
        return prob
    store.upsert_app_user({**u, "password_hash": hash_password(new_pw), "must_change_pw": must_change})
    return None


def request_access(store, email, name, message):
    email = normalize_email(email)
    if not valid_email(email):
        return "Informe um e-mail válido."
    if store.get_app_user(email):
        return "Você já tem uma conta — é só entrar."
    store.add_access_request({"email": email, "name": (name or "").strip(),
                              "message": message or "", "status": "pending"})
    store.log_audit(email, "access_request", "")
    return None


def delete_user(store, email):
    """Remove a conta E todos os dados de estudo dela."""
    email = normalize_email(email)
    for fn in ("delete_progress", "delete_answers", "delete_reviews", "delete_mocks"):
        try:
            getattr(store, fn)(email)
        except Exception:
            pass
    store.delete_app_user(email)
    store.log_audit(email, "user_deleted", "")
