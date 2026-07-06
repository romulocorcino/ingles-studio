"""Shadowing: ouça a voz nativa e repita imitando. Treino de fala e pronúncia."""
import random

import streamlit as st

from core import ui
from core.db import get_store, user_cards

store = get_store()
user = st.session_state["user"]
cards = [c for c in user_cards(user) if c["tipo"] == "flashcard"]
ss = st.session_state

st.title("🗣️ Shadowing — ouça e repita")
st.caption("Técnica de fluência: **1)** ouça a frase · **2)** repita em voz alta imitando o ritmo e a "
           "entonação · **3)** ouça devagar (🐢) e compare. Repita 3–5x cada frase.")

if not cards:
    st.warning("Sem frases ainda. Adicione em ➕ Add a card ou sincronize o deck em ⚙️ Data & sync.")
    st.stop()

skills = ["All"] + sorted({c["topico"] for c in cards})
default_ix = skills.index("Everyday Phrases") if "Everyday Phrases" in skills else 0
sel = st.selectbox("Habilidade", skills, index=default_ix)
pool = [c for c in cards if sel == "All" or c["topico"] == sel]
if not pool:
    st.info("Nada nesta habilidade.")
    st.stop()

# ordem embaralhada, reconstruída quando muda o filtro
sig = f"{sel}:{len(pool)}"
if ss.get("sh_sig") != sig:
    order = list(range(len(pool)))
    random.shuffle(order)
    ss.sh_sig, ss.sh_order, ss.sh_i = sig, order, 0

i = ss.sh_i % len(pool)
card = pool[ss.sh_order[i]]

st.progress((i + 1) / len(pool), text=f"Frase {i + 1} de {len(pool)}")
ui.card_box(ui.badge(card["topico"]) + ui.badge(card.get("subtopico") or ""), f"**{card['frente']}**")
ui.speak_button(card["frente"], label="🔊 Ouvir")

if st.toggle("👁️ Mostrar tradução", key=f"sh_t_{i}"):
    ui.answer_box(card["verso"])

c1, c2, c3 = st.columns(3)
if c1.button("← Anterior", width="stretch"):
    ss.sh_i = (i - 1) % len(pool)
    st.rerun()
if c2.button("🔀 Embaralhar", width="stretch"):
    random.shuffle(ss.sh_order)
    ss.sh_i = 0
    st.rerun()
if c3.button("Próxima →", type="primary", width="stretch"):
    ss.sh_i = i + 1
    st.rerun()
