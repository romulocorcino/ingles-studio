"""Static content: skill structure, relative skill weights and grammar reference.

Public API kept identical to the CFA app so the views work unchanged:
  TOPIC_WEIGHTS, TOPIC_ABBREV, topic_weight(), FORMULAS,
  EXAM_DEFAULT_DATE, EXAM_QUESTIONS, EXAM_SESSION_MIN, SECONDS_PER_QUESTION,
  MPS_BAND, TARGET_ACCURACY
Here "exam" is reframed as your **fluency goal** and "topics" as **skills**.
"""
import datetime as dt

# ---------------- fluency goal / timed test ----------------
EXAM_DEFAULT_DATE = dt.date.today() + dt.timedelta(days=180)  # meta de fluência (~6 meses)
EXAM_QUESTIONS = 40           # tamanho de um teste cronometrado completo
EXAM_SESSION_MIN = 20         # minutos de referência
SECONDS_PER_QUESTION = 25     # ritmo-alvo por questão (reconhecimento rápido)
MPS_BAND = (0.70, 0.80)       # faixa-alvo de acerto (fluência funcional)
TARGET_ACCURACY = 0.80        # meta de acurácia por habilidade

# Peso relativo de cada habilidade (importância no seu progresso de fluência).
# Usa o ponto médio da faixa; normalizado para somar 1.0.
TOPIC_WEIGHTS = {
    "Everyday Phrases":       (18, 22),
    "Vocabulary":             (14, 18),
    "Grammar":                (12, 16),
    "Phrasal Verbs":          (8, 12),
    "Business English":       (8, 12),
    "Pronunciation":          (8, 12),
    "Idioms & Expressions":   (6, 10),
    "Connectors & Writing":   (5, 9),
}

TOPIC_ABBREV = {
    "Everyday Phrases": "PHR", "Vocabulary": "VOC", "Grammar": "GRA",
    "Phrasal Verbs": "PHV", "Business English": "BIZ", "Pronunciation": "PRO",
    "Idioms & Expressions": "IDM", "Connectors & Writing": "CON",
}


def topic_weight(topic: str) -> float:
    """Normalized weight (sums to 1.0) using the midpoint of each range."""
    mids = {t: (lo + hi) / 2 for t, (lo, hi) in TOPIC_WEIGHTS.items()}
    total = sum(mids.values())
    return mids.get(topic, 0) / total


# ---------------- Grammar & pronunciation reference (markdown) ----------------
# (name, markdown_body, note) — rendered with st.markdown in the Reference view.
FORMULAS = {
    "Verb Tenses": [
        ("Present Simple",
         "**I / you / we / they work** · **he / she / it work*s***\n\n"
         "Rotinas, fatos e verdades gerais.\n\n"
         "> *She **works** at a bank. Water **boils** at 100°C.*",
         "3ª pessoa do singular leva -s"),
        ("Present Continuous",
         "**am / is / are + verb-ing**\n\n"
         "Ação acontecendo agora ou temporária.\n\n"
         "> *I **am studying** English right now.*",
         "agora / temporário"),
        ("Past Simple",
         "**verb-ed** (regulares) · forma própria (irregulares)\n\n"
         "Ação concluída num tempo definido no passado.\n\n"
         "> *I **worked** yesterday. She **went** home.*",
         "quando? ontem, in 2020..."),
        ("Present Perfect",
         "**have / has + past participle**\n\n"
         "Passado ligado ao presente; experiência; tempo indefinido.\n\n"
         "> *I **have lived** here for 5 years. **Have** you ever **been** to the US?*",
         "for / since / ever / already / yet"),
        ("Future — will vs going to",
         "**will + verb** -> decisao do momento / previsao\n\n"
         "**be going to + verb** -> plano / intencao\n\n"
         "> *I'**ll** help you! . I'**m going to** travel next month.*",
         "will = espontaneo; going to = planejado"),
        ("Conditionals",
         "**Zero:** If + present, present (fatos)\n\n"
         "**1st:** If + present, will + verb (real/futuro)\n\n"
         "**2nd:** If + past, would + verb (irreal/hipotetico)\n\n"
         "> *If it **rains**, we'**ll stay**. . If I **were** rich, I **would** travel.*",
         ""),
    ],
    "Irregular Verbs (top 40)": [
        ("Base -> Past -> Participle",
         "| Base | Past | Participle | PT |\n|---|---|---|---|\n"
         "| be | was/were | been | ser/estar |\n| become | became | become | tornar-se |\n"
         "| begin | began | begun | comecar |\n| break | broke | broken | quebrar |\n"
         "| bring | brought | brought | trazer |\n| buy | bought | bought | comprar |\n"
         "| choose | chose | chosen | escolher |\n| come | came | come | vir |\n"
         "| do | did | done | fazer |\n| drink | drank | drunk | beber |\n"
         "| drive | drove | driven | dirigir |\n| eat | ate | eaten | comer |\n"
         "| fall | fell | fallen | cair |\n| feel | felt | felt | sentir |\n"
         "| find | found | found | encontrar |\n| get | got | got/gotten | conseguir |\n"
         "| give | gave | given | dar |\n| go | went | gone | ir |\n"
         "| have | had | had | ter |\n| hear | heard | heard | ouvir |\n"
         "| keep | kept | kept | manter |\n| know | knew | known | saber |\n"
         "| leave | left | left | deixar/partir |\n| make | made | made | fazer |\n"
         "| meet | met | met | encontrar |\n| pay | paid | paid | pagar |\n"
         "| put | put | put | colocar |\n| read | read | read | ler |\n"
         "| run | ran | run | correr |\n| say | said | said | dizer |\n"
         "| see | saw | seen | ver |\n| sell | sold | sold | vender |\n"
         "| send | sent | sent | enviar |\n| speak | spoke | spoken | falar |\n"
         "| take | took | taken | pegar/levar |\n| teach | taught | taught | ensinar |\n"
         "| tell | told | told | contar |\n| think | thought | thought | pensar |\n"
         "| write | wrote | written | escrever |",
         "os que mais caem em prova e conversa"),
    ],
    "Pronunciation tips": [
        ("The 'TH' sounds",
         "**/theta/** (surdo): *think, three, math* -- lingua entre os dentes, sem voz.\n\n"
         "**/eth/** (sonoro): *this, the, mother* -- mesma posicao, com voz.",
         "nao vire 'f' nem 't'"),
        ("-ED endings (past)",
         "**/t/** apos som surdo: *worked, stopped*\n\n"
         "**/d/** apos som sonoro/vogal: *played, lived*\n\n"
         "**/id/** apos t/d: *wanted, needed*",
         "so vira silaba extra depois de t/d"),
        ("Word stress",
         "Substantivos: **RE**cord, **PRE**sent . Verbos: re**CORD**, pre**SENT**.\n\n"
         "A silaba tonica muda o sentido e o ritmo.",
         "ingles e stress-timed"),
    ],
    "Common confusions": [
        ("make vs do",
         "**do** = tarefas/atividades: *do homework, do the dishes*\n\n"
         "**make** = criar/produzir: *make a decision, make dinner*", ""),
        ("say vs tell",
         "**tell** + pessoa: *tell me*, *tell him*\n\n"
         "**say** (sem pessoa direta): *say something*, *say that...*", ""),
        ("False friends",
         "*actually* = na verdade (nao 'atualmente' -> **currently**)\n\n"
         "*pretend* = fingir (nao 'pretender' -> **intend**)\n\n"
         "*push* = empurrar (nao 'puxar' -> **pull**)\n\n"
         "*library* = biblioteca (nao 'livraria' -> **bookstore**)", "cuidado!"),
    ],
}
