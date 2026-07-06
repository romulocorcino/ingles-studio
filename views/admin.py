"""Admin panel: access requests, user management, everyone's progress, audit log.
Visible only to the admin."""
import pandas as pd
import streamlit as st

from core import analytics, auth, scheduler
from core.db import get_store

store = get_store()
me = st.session_state["auth_user"]

if not auth.is_admin(me):
    st.error("🔒 Acesso restrito ao administrador.")
    st.stop()

st.title("👑 Admin panel")

tab_req, tab_users, tab_prog, tab_log = st.tabs(
    ["🙋 Access requests", "👥 Users", "📊 Everyone's progress", "🧾 Audit log"])

# ============================================================ access requests
with tab_req:
    pending = store.list_access_requests("pending")
    st.caption(f"**{len(pending)}** solicitação(ões) pendente(s).")
    for r in pending:
        with st.container(border=True):
            st.markdown(f"**{r.get('name') or '—'}** · `{r.get('email')}`")
            if r.get("message"):
                st.caption(r["message"])
            c1, c2 = st.columns(2)
            if c1.button("✅ Aprovar e criar login", key=f"ap_{r['id']}", width="stretch"):
                temp = auth.temp_password()
                err = auth.create_user(store, r["email"], r.get("name", ""), temp,
                                       role="user", must_change=True)
                if err:
                    st.error(err)
                else:
                    store.update_access_request(r["id"], "approved")
                    store.log_audit(me["email"], "approve_request", r["email"])
                    st.success(f"Conta criada para `{r['email']}`.")
                    st.info(f"🔑 Senha temporária: **{temp}**  \nEnvie para a pessoa — ela troca no 1º acesso.")
            if c2.button("🗑️ Rejeitar", key=f"rj_{r['id']}", width="stretch"):
                store.update_access_request(r["id"], "rejected")
                store.log_audit(me["email"], "reject_request", r["email"])
                st.rerun()
    with st.expander("Histórico de solicitações"):
        allr = store.list_access_requests()
        if not allr:
            st.caption("Nenhuma solicitação ainda.")
        for r in allr:
            st.markdown(f"- `{r.get('email')}` — **{r.get('status')}**")

# ============================================================ users
with tab_users:
    st.subheader("➕ Adicionar usuário")
    with st.form("add_user"):
        c1, c2 = st.columns(2)
        email = c1.text_input("E-mail")
        name = c2.text_input("Nome")
        c3, c4 = st.columns(2)
        role = c3.selectbox("Papel", ["user", "admin"])
        pw = c4.text_input("Senha inicial", value=auth.temp_password(),
                          help="A pessoa troca no 1º acesso.")
        if st.form_submit_button("Criar usuário", type="primary"):
            err = auth.create_user(store, email, name, pw, role=role, must_change=True)
            if err:
                st.error(err)
            else:
                store.log_audit(me["email"], "create_user", auth.normalize_email(email))
                st.success(f"Usuário `{email}` criado. Senha inicial: **{pw}**")

    st.divider()
    st.subheader("Usuários existentes")
    for u in store.list_app_users():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.markdown(
                f"**{u.get('name') or u['email']}** · `{u['email']}`  \n"
                f"{'👑 admin' if u.get('role') == 'admin' else '👤 user'} · "
                f"{'🟢 ativo' if u.get('active') else '🔴 inativo'}"
                + (f" · {u.get('level')}" if u.get('level') else ""))
            if c2.button("🔑 Reset senha", key=f"rs_{u['email']}", width="stretch"):
                temp = auth.temp_password()
                auth.set_password(store, u["email"], temp, must_change=True)
                store.log_audit(me["email"], "reset_pw", u["email"])
                st.info(f"Nova senha de `{u['email']}`: **{temp}**")
            active = u.get("active", True)
            if c3.button("🚫 Desativar" if active else "✅ Ativar", key=f"tg_{u['email']}",
                         width="stretch"):
                full = store.get_app_user(u["email"])
                store.upsert_app_user({**full, "active": not active})
                store.log_audit(me["email"], "toggle_active", u["email"])
                st.rerun()
            if u["email"] != me["email"]:
                if c4.button("🗑️ Excluir", key=f"del_{u['email']}", width="stretch"):
                    st.session_state[f"cfd_{u['email']}"] = True
            if st.session_state.get(f"cfd_{u['email']}"):
                st.warning(f"Excluir `{u['email']}` e **todo o progresso** dessa pessoa? Não dá pra desfazer.")
                cc1, cc2 = st.columns(2)
                if cc1.button("Sim, excluir", key=f"cdel_{u['email']}"):
                    auth.delete_user(store, u["email"])
                    st.session_state.pop(f"cfd_{u['email']}", None)
                    st.rerun()
                if cc2.button("Cancelar", key=f"ccan_{u['email']}"):
                    st.session_state.pop(f"cfd_{u['email']}", None)
                    st.rerun()

# ============================================================ everyone's progress
with tab_prog:
    st.caption("Progresso de cada aluno (somente leitura).")
    rows = []
    for u in store.list_app_users():
        em = u["email"]
        ans = store.get_answers(em)
        revs = store.get_reviews(em)
        prog = store.get_progress(em)
        learned = sum(1 for p in prog.values() if (p.get("reps") or 0) >= 1)
        mature = sum(1 for p in prog.values() if scheduler.is_mature(p))
        df = analytics.answers_df(ans)
        acc = df["ok"].mean() if not df.empty else float("nan")
        rows.append({"User": u.get("name") or em, "Email": em,
                     "Streak": analytics.streak(ans, revs), "Learned": learned,
                     "Mastered": mature, "Answers": len(ans), "Accuracy": acc})
    if rows:
        st.dataframe(
            pd.DataFrame(rows), hide_index=True, width="stretch",
            column_config={"Accuracy": st.column_config.ProgressColumn(
                format="percent", min_value=0, max_value=1)})
    else:
        st.info("Nenhum usuário ainda.")

# ============================================================ audit log
with tab_log:
    log = store.list_audit(200)
    if not log:
        st.caption("Sem eventos registrados ainda.")
    else:
        st.dataframe(pd.DataFrame(log), hide_index=True, width="stretch")
