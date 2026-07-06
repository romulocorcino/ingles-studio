"""Add your own cards (flashcards or questions) — no JSON, no code.
Personal by default (only you see them); admin can also add shared cards."""
import uuid

import streamlit as st

from core import auth
from core.content import TOPIC_WEIGHTS
from core.db import cached_cards, clear_card_cache, get_store

store = get_store()
user = st.session_state["user"]
me = st.session_state["auth_user"]
admin = auth.is_admin(me)

SKILLS = list(TOPIC_WEIGHTS.keys())

st.title("➕ Add a card")
st.caption("Crie seus próprios cards. Por padrão são **seus** (só você vê) e entram "
           "automaticamente na sua revisão, prática e biblioteca."
           + (" Como admin, você também pode criar cards **compartilhados** (para todos)." if admin else ""))

kind = st.radio("Tipo de card", ["🃏 Flashcard", "❓ Questão (múltipla escolha)"], horizontal=True)
shared = False
if admin:
    shared = st.toggle("🌐 Compartilhar com todos (card comum)", value=False,
                       help="Ligado: aparece para todos os usuários. Desligado: só para você.")


def _new_id():
    return "u-" + uuid.uuid4().hex[:12]


def _save(card):
    card["owner"] = None if shared else user
    card["fonte"] = "shared" if shared else f"user:{user}"
    store.upsert_cards([card])
    clear_card_cache()
    store.log_audit(user, "add_card_shared" if shared else "add_card", card["id"])


# ---------------- flashcard ----------------
if kind.startswith("🃏"):
    with st.form("add_flash", clear_on_submit=True):
        c1, c2 = st.columns(2)
        topico = c1.selectbox("Habilidade", SKILLS)
        sub = c2.text_input("Subtópico (opcional)", placeholder="ex.: Greetings, Travel…")
        frente = st.text_input("Frente (inglês) *", placeholder="ex.: Break a leg!")
        verso = st.text_area("Verso (tradução / dica) *", height=100,
                             placeholder="ex.: **Boa sorte!** (antes de se apresentar)")
        diff = st.select_slider("Dificuldade", options=[1, 2, 3, 4, 5], value=2)
        if st.form_submit_button("💾 Salvar flashcard", type="primary"):
            if not frente.strip() or not verso.strip():
                st.error("Preencha a frente e o verso.")
            else:
                _save({"id": _new_id(), "tipo": "flashcard", "topico": topico,
                       "subtopico": sub.strip(), "dificuldade": int(diff), "tags": [],
                       "frente": frente.strip(), "verso": verso.strip()})
                st.success("Flashcard salvo ✓ Já está na sua revisão.")

# ---------------- question ----------------
else:
    with st.form("add_q", clear_on_submit=True):
        c1, c2 = st.columns(2)
        topico = c1.selectbox("Habilidade", SKILLS)
        sub = c2.text_input("Subtópico (opcional)", placeholder="ex.: Prepositions")
        enun = st.text_area("Enunciado / pergunta *", height=80,
                            placeholder="ex.: She's good ___ playing guitar.")
        o1 = st.text_input("Opção A *")
        o2 = st.text_input("Opção B *")
        o3 = st.text_input("Opção C (opcional)")
        correct = st.radio("Resposta correta *", ["A", "B", "C"], horizontal=True)
        expl = st.text_area("Explicação (opcional)", height=70,
                            placeholder="Por que essa é a resposta certa?")
        diff = st.select_slider("Dificuldade", options=[1, 2, 3, 4, 5], value=3)
        if st.form_submit_button("💾 Salvar questão", type="primary"):
            opts = [o1.strip(), o2.strip()] + ([o3.strip()] if o3.strip() else [])
            idx = {"A": 0, "B": 1, "C": 2}[correct]
            if not enun.strip() or not o1.strip() or not o2.strip():
                st.error("Preencha o enunciado e pelo menos as opções A e B.")
            elif idx >= len(opts):
                st.error("Você marcou a opção C como correta, mas ela está vazia.")
            else:
                _save({"id": _new_id(), "tipo": "questao", "topico": topico,
                       "subtopico": sub.strip(), "dificuldade": int(diff), "tags": [],
                       "enunciado": enun.strip(), "opcoes": opts, "correta": idx,
                       "explicacao": expl.strip()})
                st.success("Questão salva ✓ Já está na Prática e no Teste de nível.")

# ---------------- my cards ----------------
st.divider()
st.subheader("🗂️ Meus cards")
mine = [c for c in cached_cards() if c.get("owner") == user]
if not mine:
    st.caption("Você ainda não criou cards. Crie o primeiro acima! 👆")
else:
    st.caption(f"{len(mine)} card(s) criado(s) por você.")
    for c in mine:
        with st.container(border=True):
            cc1, cc2 = st.columns([6, 1])
            content = c.get("frente") or c.get("enunciado") or ""
            icon = "🃏" if c["tipo"] == "flashcard" else "❓"
            cc1.markdown(f"{icon} **{content}**  \n<span style='opacity:.7;font-size:.85rem'>"
                         f"{c['topico']} · {c.get('subtopico') or ''}</span>", unsafe_allow_html=True)
            if cc2.button("🗑️", key=f"del_{c['id']}", help="Excluir este card"):
                store.delete_card(c["id"])
                clear_card_cache()
                store.log_audit(user, "delete_card", c["id"])
                st.rerun()

if admin:
    st.divider()
    shared_cards = [c for c in cached_cards() if c.get("owner")]
    st.caption(f"👑 Admin: há {len([c for c in cached_cards() if not c.get('owner')])} cards "
               f"compartilhados e {len(shared_cards)} pessoais (de todos os usuários).")
