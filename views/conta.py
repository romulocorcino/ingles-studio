"""My account: profile + change your own password."""
import streamlit as st

from core import auth
from core.db import get_store

store = get_store()
user = st.session_state["auth_user"]

st.title("👤 My account")

c1, c2 = st.columns(2)
c1.markdown(f"**Name:** {user.get('name') or '—'}")
c1.markdown(f"**Email:** `{user.get('email')}`")
c2.markdown(f"**Role:** {'👑 Admin' if auth.is_admin(user) else '👤 Student'}")
if user.get("level"):
    c2.markdown(f"**Level:** {user['level']}")

st.divider()
st.subheader("🔑 Change password")
with st.form("change_pw"):
    old = st.text_input("Current password", type="password")
    new = st.text_input("New password", type="password",
                        help=f"At least {auth.MIN_PW} characters, with letters and numbers.")
    new2 = st.text_input("Confirm new password", type="password")
    if st.form_submit_button("Update password", type="primary"):
        if new != new2:
            st.error("As senhas não conferem.")
        else:
            err = auth.change_password(store, user["email"], old, new)
            if err:
                st.error(err)
            else:
                st.session_state["auth_user"] = store.get_app_user(user["email"])
                st.success("Senha atualizada com sucesso ✓")
