"""Explicação por IA (Claude) sob demanda.

Opcional: só ativa se houver ANTHROPIC_API_KEY nos secrets do Streamlit.
Sem a chave, o recurso fica invisível e o app funciona normalmente.
"""
import streamlit as st


def _key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def _model():
    try:
        return st.secrets.get("ANTHROPIC_MODEL") or "claude-opus-4-8"
    except Exception:
        return "claude-opus-4-8"


def available():
    return bool(_key())


@st.cache_data(ttl=86400, show_spinner=False)
def explain(card_id, kind, front, back, options, correct, explicacao, topico):
    """Explicação didática em PT, cacheada por card (24h)."""
    key = _key()
    if not key:
        return None
    try:
        import anthropic
    except Exception:
        return "A biblioteca 'anthropic' não está instalada no servidor."

    if kind == "questao":
        opts = list(options or [])
        certa = opts[correct] if (opts and correct is not None and correct < len(opts)) else ""
        detail = (f"Habilidade: {topico}\nPergunta: {front}\nOpções: {opts}\n"
                  f"Resposta correta: {certa}\nExplicação curta atual: {explicacao or '(nenhuma)'}")
    else:
        detail = f"Habilidade: {topico}\nInglês: {front}\nTradução/dica atual: {back}"

    prompt = (
        "Você é um professor de inglês para brasileiros. Explique de forma clara, curta e "
        "didática, em PORTUGUÊS. Foque na REGRA por trás (tempo verbal e por que o verbo muda, "
        "substantivo contável/incontável, artigo, preposição, colocação). Se houver opções, "
        "explique por que a certa está certa e por que as outras estão erradas. Termine com "
        "1 exemplo natural extra em inglês + tradução. Máx. ~130 palavras, use markdown.\n\n"
        + detail)

    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=_model(), max_tokens=700,
            messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in msg.content if b.type == "text").strip()
    except Exception as e:
        return f"Não consegui gerar a explicação agora ({type(e).__name__}). Tente de novo."
