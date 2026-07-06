# English Studio 🇬🇧

App de estudo de inglês no mesmo molde do "CFA Study Studio": **repetição espaçada
(FSRS)**, prática adaptativa, teste cronometrado de nível, caderno de erros, dashboard
de fluência e **pronúncia nativa** (Text-to-Speech). Streamlit + Supabase (ou SQLite local).

## Funcionalidades

- **🔁 Revisão FSRS** — o algoritmo de repetição espaçada do Anki moderno (estabilidade
  + dificuldade por card), intervalo previsto em cada botão, undo e suspensão de cards.
- **🔊 Pronúncia nativa** — botão "Listen" em cada card usa a voz do navegador (Web Speech),
  com opção devagar (🐢). Sem arquivos de áudio, funciona offline.
- **🎯 Prática adaptativa** — prioriza automaticamente o que você mais erra.
- **📝 Teste cronometrado de nível** — ritmo de conversa, navegador de questões, marcar p/ revisão.
- **📒 Caderno de erros** — toda questão errada fica pendente até você acertar de novo.
- **🏠 Dashboard de fluência** — prontidão 0–100% ponderada pelo peso de cada habilidade.
- **📊 Desempenho** — tendência de acurácia, acurácia por habilidade vs. meta, carga futura de revisões.
- **📅 Plano de estudo** — meta de fluência, metas diárias, fases e priorização peso × lacuna.
- **📐 Referência de gramática** — tempos verbais, verbos irregulares, dicas de pronúncia, false friends.

## Habilidades (decks)

Everyday Phrases · Vocabulary · Grammar · Phrasal Verbs · Business English ·
Pronunciation · Idioms & Expressions · Connectors & Writing.

## Rodando

### Local (zero configuração)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Sem Supabase configurado, roda em **modo local** (SQLite em `local_data.db`).
O deck é semeado automaticamente no primeiro uso.

### Produção (progresso sincronizado entre aparelhos)

1. **Supabase** — crie um projeto grátis em supabase.com → SQL Editor → cole `schema.sql` → Run.
   Em Project Settings → API copie a *Project URL* e a *anon key*.
2. **Streamlit Cloud** — share.streamlit.io → New app → este repo, branch `main`, `app.py` →
   Settings → Secrets:
   ```toml
   SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
   SUPABASE_KEY = "sua-anon-key"
   ```
3. No app: **⚙️ Data & sync → Sync cards from the repository**.

O app é acessível do celular pela URL do Streamlit Cloud (dá pra "Adicionar à tela inicial").

## Conteúdo

O deck é versionado em `seed_cards.json`. Para adicionar/editar, mude as listas em
`build_seed.py` e rode `python build_seed.py`, depois **Sync** no app. Campos (chaves em
português por compatibilidade; valores em inglês):

```jsonc
{ "id": "skill-sub-001", "tipo": "flashcard|questao|conceito",
  "topico": "Everyday Phrases", "subtopico": "Greetings", "dificuldade": 1-5,
  "frente": "Hi, nice to meet you!", "verso": "**Oi, prazer...**",   // flashcard/conceito
  "enunciado": "...", "opcoes": ["A","B","C"], "correta": 1, "explicacao": "..." }  // questao
```

## Arquitetura

```
app.py            navegação, sidebar, bootstrap
core/content.py   habilidades + pesos, referência de gramática, meta
core/scheduler.py FSRS-4.5 (new/learning/review/relearning)
core/db.py        SupabaseStore + LocalStore (SQLite) intercambiáveis
core/analytics.py prontidão ponderada, streak, séries, caderno de erros
core/ui.py        CSS, componentes, sessão de quiz e botão de pronúncia (TTS)
views/            uma página por arquivo (st.navigation)
build_seed.py     gera seed_cards.json a partir de listas estruturadas
```
