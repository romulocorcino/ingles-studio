"""English Studio — Streamlit + Supabase, com login por usuário e admin."""
import datetime as dt
import json
import os

import streamlit as st

from core import analytics, auth, ui
from core.content import EXAM_DEFAULT_DATE
from core.db import cached_cards, clear_card_cache, get_store

st.set_page_config(page_title="English Studio", page_icon="🇬🇧",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

store = get_store()

# ---------------- first run: auto-seed the deck ----------------
if not cached_cards():
    seed_path = os.path.join(os.path.dirname(__file__), "seed_cards.json")
    if os.path.exists(seed_path):
        seed = json.load(open(seed_path, encoding="utf-8"))["cards"]
        store.upsert_cards(seed)
        clear_card_cache()


# ============================================================ LOGIN GATE
def _login_screen():
    st.markdown("<div style='max-width:460px;margin:2rem auto'>", unsafe_allow_html=True)
    st.title("🇬🇧 English Studio")
    st.caption("Entre com sua conta para estudar. Seu progresso é pessoal e sincronizado.")
    tab_in, tab_req = st.tabs(["🔑 Entrar", "🙋 Solicitar acesso"])

    with tab_in:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            pw = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", type="primary", use_container_width=True):
                user, err = auth.authenticate(store, email, pw)
                if err:
                    st.error(err)
                else:
                    st.session_state["auth_email"] = auth.normalize_email(email)
                    st.rerun()

    with tab_req:
        st.caption("Não tem conta? Peça acesso ao administrador — você recebe o login quando for aprovado.")
        with st.form("req_form"):
            name = st.text_input("Seu nome")
            remail = st.text_input("Seu e-mail")
            level = st.selectbox("Seu nível de inglês", ["Iniciante", "Intermediário", "Avançado", "Não sei"])
            msg = st.text_area("Mensagem (opcional)", placeholder="Conte por que quer usar o app…", height=80)
            if st.form_submit_button("Enviar solicitação", type="primary", use_container_width=True):
                err = auth.request_access(store, remail, name, f"[nível: {level}] {msg}".strip())
                if err:
                    st.warning(err)
                else:
                    st.success("Solicitação enviada! ✅ O administrador vai avaliar e liberar seu acesso.")
    st.markdown("</div>", unsafe_allow_html=True)


def _force_change_screen(user):
    st.markdown("<div style='max-width:460px;margin:2rem auto'>", unsafe_allow_html=True)
    st.title("🔐 Defina sua senha")
    st.info("Por segurança, troque a senha inicial antes de continuar.")
    with st.form("force_change"):
        new = st.text_input("Nova senha", type="password", help=f"Mínimo {auth.MIN_PW} caracteres, com letras e números.")
        new2 = st.text_input("Confirme a nova senha", type="password")
        if st.form_submit_button("Salvar e entrar", type="primary", use_container_width=True):
            if new != new2:
                st.error("As senhas não conferem.")
            else:
                err = auth.set_password(store, user["email"], new, must_change=False)
                if err:
                    st.error(err)
                else:
                    store.log_audit(user["email"], "password_change_forced", "")
                    st.success("Senha definida! Entrando…")
                    st.rerun()
    if st.button("Sair"):
        st.session_state.pop("auth_email", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# resolve sessão
auth_email = st.session_state.get("auth_email")
current = store.get_app_user(auth_email) if auth_email else None
if not current or not current.get("active", True):
    st.session_state.pop("auth_email", None)
    _login_screen()
    st.stop()
if current.get("must_change_pw"):
    _force_change_screen(current)
    st.stop()

# autenticado
st.session_state["user"] = auth.normalize_email(current["email"])   # progresso é keyed por e-mail
st.session_state["auth_user"] = current
user = st.session_state["user"]

# ---------------- global sidebar ----------------
with st.sidebar:
    st.title("🇬🇧 English Studio")
    role_badge = "👑 Admin" if auth.is_admin(current) else "👤 Aluno"
    st.markdown(f"**{current.get('name') or user}**  \n<span class='badge blue'>{role_badge}</span>  "
                f"<span class='badge'>{user}</span>", unsafe_allow_html=True)
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.pop("auth_email", None)
        st.session_state.pop("auth_user", None)
        st.rerun()

    settings = store.get_settings(user)
    st.session_state["settings"] = settings
    goal_date = dt.date.fromisoformat(settings["exam_date"]) if settings.get("exam_date") else EXAM_DEFAULT_DATE
    days_left = max(0, (goal_date - dt.date.today()).days)

    answers = store.get_answers(user)
    reviews = store.get_reviews(user)
    stk = analytics.streak(answers, reviews)

    c1, c2 = st.columns(2)
    c1.metric("🎯 Days to goal", days_left)
    c2.metric("🔥 Streak", f"{stk}d")

    mode_txt = ("☁️ Supabase — progress synced across devices" if store.mode == "supabase"
                else "💻 Local mode — data stays on this computer")
    st.caption(mode_txt)

# ---------------- navigation ----------------
pages = {
    "Study": [
        st.Page("views/dashboard.py", title="Dashboard", icon="🏠", default=True),
        st.Page("views/revisar.py", title="Review (spaced repetition)", icon="🔁"),
        st.Page("views/praticar.py", title="Practice", icon="🎯"),
        st.Page("views/simulado.py", title="Timed level test", icon="📝"),
        st.Page("views/erros.py", title="Mistakes notebook", icon="📒"),
    ],
    "Track": [
        st.Page("views/desempenho.py", title="Performance", icon="📊"),
        st.Page("views/plano.py", title="Study plan", icon="📅"),
    ],
    "Reference": [
        st.Page("views/biblioteca.py", title="Library", icon="📖"),
        st.Page("views/referencia.py", title="Grammar reference", icon="📐"),
        st.Page("views/dados.py", title="Data & sync", icon="⚙️"),
    ],
    "Account": [
        st.Page("views/conta.py", title="My account", icon="👤"),
    ],
}
if auth.is_admin(current):
    pages["Admin"] = [st.Page("views/admin.py", title="Admin panel", icon="👑")]

st.navigation(pages).run()
