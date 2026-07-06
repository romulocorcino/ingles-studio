"""Gera o seed_cards.json do English Studio a partir de listas estruturadas.

Rode:  python build_seed.py
Edite as listas abaixo para adicionar conteudo e rode de novo.
"""
import json
import os

cards = []


def _verso(pt, ipa="", ex="", tip=""):
    parts = [f"**{pt}**"]
    if ipa:
        parts.append(f"/{ipa}/")
    if ex:
        parts.append(f"_“{ex}”_")
    if tip:
        parts.append(f"💡 {tip}")
    return "\n\n".join(parts)


def add_flashcard(topico, sub, en, pt, ipa="", ex="", tip="", diff=2, tags=None):
    cid = f"{topico[:3].lower()}-{sub[:3].lower()}-f{len([c for c in cards if c['tipo']=='flashcard'])+1:03d}"
    cards.append({
        "id": cid, "tipo": "flashcard", "topico": topico, "subtopico": sub,
        "dificuldade": diff, "tags": tags or [], "fonte": "English Studio",
        "frente": en, "verso": _verso(pt, ipa, ex, tip),
    })


def add_concept(topico, sub, frente, verso, diff=2, tags=None):
    cid = f"{topico[:3].lower()}-{sub[:3].lower()}-c{len([c for c in cards if c['tipo']=='conceito'])+1:03d}"
    cards.append({
        "id": cid, "tipo": "conceito", "topico": topico, "subtopico": sub,
        "dificuldade": diff, "tags": tags or [], "fonte": "English Studio",
        "frente": frente, "verso": verso,
    })


def add_question(topico, sub, enunciado, opcoes, correta, explicacao, diff=3, tags=None):
    cid = f"{topico[:3].lower()}-{sub[:3].lower()}-q{len([c for c in cards if c['tipo']=='questao'])+1:03d}"
    cards.append({
        "id": cid, "tipo": "questao", "topico": topico, "subtopico": sub,
        "dificuldade": diff, "tags": tags or [], "fonte": "English Studio",
        "enunciado": enunciado, "opcoes": opcoes, "correta": correta,
        "explicacao": explicacao,
    })


# =====================================================================
# 1) EVERYDAY PHRASES  (en, pt, ipa, ex, tip, diff)
# =====================================================================
EVERYDAY = {
    "Greetings": [
        ("Hi, nice to meet you!", "Oi, prazer em conhecer você!", "haɪ naɪs tu miːt juː", "Hi, nice to meet you! I'm Ana.", "", 1),
        ("How are you doing?", "Como você está? / Como vai?", "haʊ ɑːr juː ˈduːɪŋ", "", "", 1),
        ("I'm doing great, thanks!", "Estou muito bem, obrigado!", "", "", "", 1),
        ("What's your name?", "Qual é o seu nome?", "wɒts jɔːr neɪm", "", "", 1),
        ("Where are you from?", "De onde você é?", "", "", "", 1),
        ("Long time no see!", "Quanto tempo!", "", "", "Informal, muito comum.", 2),
        ("Take care!", "Se cuida!", "teɪk keər", "", "", 1),
        ("How have you been?", "Como você tem passado?", "", "", "Para quem você não vê há um tempo.", 2),
    ],
    "Small talk": [
        ("What do you do for a living?", "O que você faz da vida? (trabalho)", "", "", "", 2),
        ("What are you up to?", "O que você está aprontando/fazendo?", "", "", "Informal, super comum.", 2),
        ("That makes sense.", "Isso faz sentido.", "", "", "", 1),
        ("I couldn't agree more.", "Concordo plenamente.", "", "", "", 3),
        ("To be honest with you...", "Para ser sincero com você...", "", "", "", 2),
        ("By the way, ...", "A propósito, ... / Aliás, ...", "baɪ ðə weɪ", "", "", 1),
        ("Never mind.", "Deixa pra lá.", "ˈnevər maɪnd", "", "", 1),
        ("What do you mean?", "O que você quer dizer?", "", "", "", 1),
        ("Could you say that again?", "Você poderia repetir?", "", "", "", 1),
        ("Sounds good to me.", "Por mim, tudo bem.", "", "", "", 1),
        ("It's up to you.", "A decisão é sua. / Você que sabe.", "", "", "", 2),
        ("I'm just kidding.", "Estou só brincando.", "", "", "", 1),
    ],
    "Restaurant": [
        ("A table for two, please.", "Uma mesa para dois, por favor.", "", "", "", 1),
        ("Could I see the menu?", "Posso ver o cardápio?", "", "", "", 1),
        ("What do you recommend?", "O que você recomenda?", "", "", "", 1),
        ("Can I get the check, please?", "Pode trazer a conta, por favor?", "", "", "'check' (EUA) / 'bill' (UK).", 1),
        ("I'm allergic to peanuts.", "Eu sou alérgico a amendoim.", "", "", "", 2),
        ("This is delicious!", "Isso está delicioso!", "ðɪs ɪz dɪˈlɪʃəs", "", "", 1),
        ("I'd like it to go, please.", "Eu queria para viagem, por favor.", "", "", "", 2),
        ("Keep the change.", "Pode ficar com o troco.", "", "", "", 2),
    ],
    "Travel": [
        ("Where is the boarding gate?", "Onde fica o portão de embarque?", "", "", "", 2),
        ("I have a connecting flight.", "Eu tenho um voo de conexão.", "", "", "", 2),
        ("Is this seat taken?", "Este assento está ocupado?", "", "", "", 1),
        ("How do I get to downtown?", "Como eu chego ao centro?", "", "", "", 2),
        ("My luggage is missing.", "Minha bagagem sumiu.", "", "", "", 2),
        ("I'm just passing through.", "Estou só de passagem.", "", "", "", 2),
    ],
    "Shopping": [
        ("How much does it cost?", "Quanto custa?", "haʊ mʌtʃ dʌz ɪt kɒst", "", "", 1),
        ("Do you have this in a larger size?", "Você tem isso num tamanho maior?", "", "", "", 2),
        ("Can I try it on?", "Posso experimentar?", "", "", "", 1),
        ("I'm just looking, thanks.", "Só estou olhando, obrigado.", "", "", "", 1),
        ("Is it on sale?", "Está em promoção?", "", "", "", 1),
        ("Can I get a refund?", "Posso pedir reembolso?", "", "", "", 2),
        ("I'll take it.", "Eu vou levar.", "", "", "", 1),
    ],
    "Emergencies": [
        ("I need help!", "Eu preciso de ajuda!", "", "", "", 1),
        ("Call an ambulance!", "Chame uma ambulância!", "", "", "", 1),
        ("I don't feel well.", "Não estou me sentindo bem.", "", "", "", 1),
        ("Where is the nearest hospital?", "Onde fica o hospital mais próximo?", "", "", "", 2),
        ("It hurts here.", "Dói aqui.", "", "", "", 1),
        ("I lost my passport.", "Eu perdi meu passaporte.", "", "", "", 2),
    ],
    "Directions": [
        ("How do I get there?", "Como eu chego lá?", "", "", "", 1),
        ("Is it far from here?", "É longe daqui?", "", "", "", 1),
        ("Go straight ahead.", "Siga em frente.", "ɡoʊ streɪt əˈhed", "", "", 1),
        ("It's just around the corner.", "Fica logo ali na esquina.", "", "", "", 2),
        ("I think I'm lost.", "Acho que estou perdido.", "", "", "", 1),
        ("It's a five-minute walk.", "É uns cinco minutos a pé.", "", "", "", 2),
    ],
    "Feelings": [
        ("I'm thrilled about it.", "Estou empolgadíssimo com isso.", "", "", "", 3),
        ("That's frustrating.", "Isso é frustrante.", "", "", "", 2),
        ("I feel like having pizza.", "Estou a fim de pizza.", "", "", "'feel like + -ing' = estar a fim de.", 2),
        ("I can't wait!", "Mal posso esperar!", "", "", "", 1),
        ("I'm over the moon.", "Estou nas nuvens / radiante.", "", "", "Idiomático = muito feliz.", 3),
        ("That's a relief.", "Que alívio.", "", "", "", 2),
    ],
    "Time & weather": [
        ("What time is it?", "Que horas são?", "", "", "", 1),
        ("It's half past three.", "São três e meia.", "", "", "", 2),
        ("It's freezing outside.", "Está congelando lá fora.", "", "", "", 1),
        ("I'm running late.", "Estou atrasado.", "", "", "", 1),
        ("See you the day after tomorrow.", "Até depois de amanhã.", "", "", "", 2),
        ("Let's meet at noon.", "Vamos nos encontrar ao meio-dia.", "", "", "", 1),
    ],
}

# =====================================================================
# 2) BUSINESS ENGLISH (work)
# =====================================================================
BUSINESS = [
    ("Let's get started.", "Vamos começar.", "", "", "", 1),
    ("Can everyone hear me?", "Todos conseguem me ouvir?", "", "", "", 1),
    ("Let's circle back on that.", "Vamos retomar isso depois.", "", "", "Jargão corporativo.", 3),
    ("I'll get back to you.", "Eu te retorno.", "", "", "", 2),
    ("Let's touch base next week.", "Vamos nos alinhar na semana que vem.", "", "", "", 3),
    ("Could you walk me through it?", "Você poderia me explicar passo a passo?", "", "", "", 3),
    ("That's out of scope.", "Isso está fora do escopo.", "", "", "", 3),
    ("I'm on it.", "Já estou cuidando disso.", "", "", "", 2),
    ("Let me double-check.", "Deixa eu conferir de novo.", "", "", "", 2),
    ("What are the next steps?", "Quais são os próximos passos?", "", "", "", 2),
    ("Let's wrap up.", "Vamos encerrar/finalizar.", "", "", "", 2),
    ("Let's keep it brief.", "Vamos ser breves.", "", "", "", 2),
]

# =====================================================================
# 3) VOCABULARY
# =====================================================================
VOCAB = [
    ("although", "embora / apesar de", "ɔːlˈðoʊ", "Although it was raining, we went out.", "", 2),
    ("however", "no entanto / porém", "haʊˈevər", "", "", 2),
    ("actually", "na verdade", "ˈæktʃuəli", "", "NÃO significa 'atualmente'!", 1),
    ("currently", "atualmente", "ˈkɜːrəntli", "", "", 2),
    ("meanwhile", "enquanto isso", "", "", "", 2),
    ("therefore", "portanto", "ˈðerfɔːr", "", "", 2),
    ("besides", "além disso", "", "", "", 2),
    ("regardless", "independentemente", "", "", "", 3),
    ("awkward", "constrangedor / estranho", "ˈɔːkwərd", "", "", 2),
    ("reliable", "confiável", "rɪˈlaɪəbl", "", "", 2),
    ("overwhelming", "avassalador / muito intenso", "", "", "", 3),
    ("straightforward", "simples / direto", "", "", "", 2),
    ("insight", "percepção / entendimento profundo", "", "", "", 3),
    ("willing", "disposto (a fazer algo)", "", "Are you willing to help?", "", 2),
    ("to afford", "poder pagar / ter condições de", "", "I can't afford a new car.", "", 2),
    ("to improve", "melhorar", "ɪmˈpruːv", "", "", 1),
    ("to achieve", "alcançar / conquistar", "əˈtʃiːv", "", "", 2),
    ("to avoid", "evitar", "əˈvɔɪd", "", "", 2),
    ("worth", "que vale a pena", "wɜːrθ", "It's worth trying.", "", 2),
    ("issue", "problema / questão", "ˈɪʃuː", "", "", 1),
]

# =====================================================================
# 4) PHRASAL VERBS
# =====================================================================
PHRASAL = [
    ("give up", "desistir", "", "Don't give up on your dreams.", "", 2),
    ("figure out", "descobrir / entender (resolver)", "", "I can't figure out this problem.", "", 2),
    ("look forward to", "ansiar por / aguardar com expectativa", "", "I look forward to your reply.", "", 2),
    ("come up with", "bolar / inventar (ideia)", "", "She came up with a great idea.", "", 3),
    ("run out of", "ficar sem (acabar)", "", "We ran out of milk.", "", 2),
    ("put off", "adiar / procrastinar", "", "Don't put off until tomorrow.", "", 2),
    ("get along with", "se dar bem com (alguém)", "", "I get along with my coworkers.", "", 2),
    ("bring up", "mencionar / trazer à tona", "", "He brought up a good point.", "", 3),
    ("work out", "dar certo / malhar", "", "It all worked out in the end.", "", 2),
    ("look up", "pesquisar / procurar (info)", "", "Look up the word in a dictionary.", "", 2),
    ("turn down", "recusar / abaixar (volume)", "", "She turned down the offer.", "", 2),
    ("show up", "aparecer / comparecer", "", "He didn't show up to the meeting.", "", 2),
    ("find out", "descobrir (saber)", "", "I found out the truth.", "", 2),
    ("carry on", "continuar / seguir em frente", "", "Carry on with your work.", "", 2),
    ("get over", "superar (algo/alguém)", "", "It took months to get over it.", "", 3),
]

# =====================================================================
# 5) IDIOMS
# =====================================================================
IDIOMS = [
    ("It's a piece of cake.", "É moleza / muito fácil.", "", "", "Tarefa muito fácil.", 2),
    ("Break a leg!", "Boa sorte! (antes de se apresentar)", "", "", "Nunca traduza ao pé da letra!", 2),
    ("It's not my cup of tea.", "Não é muito a minha praia.", "", "", "", 3),
    ("Hit the nail on the head.", "Acertar em cheio.", "", "", "", 3),
    ("Once in a blue moon.", "Uma vez na vida (raramente).", "", "", "", 3),
    ("Bite the bullet.", "Encarar algo difícil / engolir o sapo.", "", "", "", 3),
    ("Cost an arm and a leg.", "Custar os olhos da cara.", "", "", "", 3),
    ("It rings a bell.", "Isso me soa familiar.", "", "", "", 3),
    ("Let's call it a day.", "Vamos parar por hoje.", "", "", "", 2),
    ("Speak of the devil!", "Falando no diabo!", "", "", "Quando a pessoa aparece.", 3),
]

# =====================================================================
# 6) PRONUNCIATION (minimal pairs / tricky sounds)
# =====================================================================
PRONUN = [
    ("ship / sheep", "navio / ovelha", "ʃɪp / ʃiːp", "", "Vogal curta /ɪ/ vs longa /iː/.", 2),
    ("live / leave", "morar / partir", "lɪv / liːv", "", "/ɪ/ curto vs /iː/ longo.", 2),
    ("beach / bitch", "praia / (palavrão)", "biːtʃ / bɪtʃ", "", "Cuidado! /iː/ vs /ɪ/.", 3),
    ("think / sink", "pensar / afundar", "θɪŋk / sɪŋk", "", "/θ/ (língua nos dentes) vs /s/.", 2),
    ("three / tree", "três / árvore", "θriː / triː", "", "/θ/ vs /t/.", 2),
    ("work / walk", "trabalhar / caminhar", "wɜːrk / wɔːk", "", "/ɜːr/ vs /ɔː/.", 2),
    ("comfortable", "confortável", "ˈkʌmftəbl", "", "Só 3 sílabas: KUMF-ta-bl.", 2),
    ("Wednesday", "quarta-feira", "ˈwenzdeɪ", "", "O 'd' é mudo: WENZ-day.", 2),
    ("clothes", "roupas", "kloʊðz", "", "Quase 'close' — não pronuncie o 'th' forte.", 3),
    ("colonel", "coronel", "ˈkɜːrnl", "", "Pronuncia-se 'kernel'!", 3),
]

# =====================================================================
# 7) CONNECTORS & WRITING
# =====================================================================
CONNECTORS = [
    ("In addition, ...", "Além disso, ...", "", "", "Adiciona informação.", 2),
    ("On the other hand, ...", "Por outro lado, ...", "", "", "Contraste.", 2),
    ("As a result, ...", "Como resultado, ...", "", "", "Consequência.", 2),
    ("For instance, ...", "Por exemplo, ...", "", "", "= for example.", 1),
    ("In other words, ...", "Em outras palavras, ...", "", "", "Reformular.", 2),
    ("Nevertheless, ...", "Mesmo assim / no entanto, ...", "", "", "Contraste formal.", 3),
    ("To sum up, ...", "Resumindo, ...", "", "", "Conclusão.", 2),
    ("Due to ...", "Devido a ...", "", "Due to the rain, the game was canceled.", "+ substantivo.", 2),
]

# =====================================================================
# 8) GRAMMAR CONCEPTS (frente -> verso)
# =====================================================================
GRAMMAR_CONCEPTS = [
    ("Quando usar Present Perfect vs Past Simple?",
     "**Past Simple**: tempo definido no passado (*I saw him yesterday*).\n\n"
     "**Present Perfect**: tempo indefinido ou ligado ao presente (*I have seen that movie*). "
     "Use com *for/since/ever/already/yet/just*.", 3),
    ("some vs any",
     "**some**: frases afirmativas e ofertas/pedidos (*I have some money. Want some coffee?*).\n\n"
     "**any**: negativas e perguntas (*I don't have any money. Do you have any questions?*).", 2),
    ("much vs many",
     "**much** + incontáveis (*much water, much time*).\n\n"
     "**many** + contáveis no plural (*many people, many books*).\n\n"
     "Em afirmativas prefira *a lot of*.", 2),
    ("Comparativos e superlativos",
     "Curtos: *tall -> taller -> the tallest*.\n\n"
     "Longos: *expensive -> more expensive -> the most expensive*.\n\n"
     "Irregulares: *good -> better -> best*; *bad -> worse -> worst*.", 2),
    ("Gerund vs Infinitive",
     "Após preposições e certos verbos use **-ing**: *enjoy doing, good at swimming*.\n\n"
     "Após *want/need/decide/would like* use **to + verbo**: *I want to go*.", 3),
    ("Artigo: a / an / the",
     "**a/an** = indefinido (algo genérico); **an** antes de som de vogal (*an hour, a university*).\n\n"
     "**the** = definido (algo específico já conhecido).", 2),
]

# =====================================================================
# 9) QUESTIONS (multiple choice)
# =====================================================================
QUESTIONS = [
    ("Grammar", "Tenses", "Choose the correct sentence:",
     ["I have seen him yesterday.", "I saw him yesterday.", "I seen him yesterday."], 1,
     "Verbo: com um tempo definido no passado ('yesterday') usa-se o **Past Simple** (saw). 'have seen' (present perfect) não combina com tempo definido.", 2),
    ("Grammar", "Present Perfect", "I ___ in São Paulo for ten years (and still live here).",
     ["live", "lived", "have lived"], 2,
     "Verbo: ação que começou no passado e **continua até agora** → **Present Perfect** (have/has + particípio): *have lived*. 'for' marca a duração.", 3),
    ("Grammar", "Prepositions", "She's really good ___ playing the guitar.",
     ["in", "at", "on"], 1, "Preposição + verbo: 'be **good at** + **-ing**': *good at **playing***.", 2),
    ("Grammar", "Articles", "I need to buy ___ umbrella.",
     ["a", "an", "the"], 1, "Artigo: usa-se **an** antes de **som de vogal**. 'umbrella' começa com o som /ʌ/ → **an** umbrella.", 2),
    ("Grammar", "Quantifiers", "There isn't ___ milk in the fridge.",
     ["some", "any", "many"], 1, "Substantivo/quantificador: em **negativas e perguntas** usa-se **any**; em afirmativas, **some**.", 2),
    ("Vocabulary", "False friends", "'Actually' significa:",
     ["atualmente", "na verdade", "de fato agora"], 1,
     "'Actually' = na verdade. 'Atualmente' = currently.", 2),
    ("Vocabulary", "False friends", "How do you say 'puxar' in English?",
     ["push", "pull", "put"], 1, "'pull' = puxar; 'push' = empurrar.", 2),
    ("Vocabulary", "Word choice", "This restaurant is expensive. I can't ___ it.",
     ["afford", "spend", "pay"], 0, "'afford' = ter condições de pagar.", 3),
    ("Phrasal Verbs", "Meaning", "'I can't figure out this problem' means I can't ___ it.",
     ["give up", "understand/solve", "postpone"], 1, "'figure out' = descobrir/entender/resolver.", 2),
    ("Phrasal Verbs", "Meaning", "She decided to ___ the job offer (recusar).",
     ["turn down", "show up", "look up"], 0, "'turn down' = recusar.", 2),
    ("Idioms & Expressions", "Meaning", "'It's a piece of cake' means it's very ___.",
     ["difficult", "easy", "expensive"], 1, "'a piece of cake' = muito fácil.", 2),
    ("Pronunciation", "Sounds", "Which word has the /iː/ (long) sound?",
     ["ship", "sheep", "sit"], 1, "'sheep' tem a vogal longa /iː/; 'ship'/'sit' têm /ɪ/.", 3),
    ("Everyday Phrases", "Usage", "A polite way to ask someone to repeat:",
     ["Say again?", "Could you say that again, please?", "What you said?"], 1,
     "Forma educada e natural.", 1),
    ("Grammar", "Conditionals", "If I ___ rich, I would travel the world.",
     ["am", "was", "were"], 2, "Verbo: no **2nd conditional** (situação hipotética/irreal) usa-se **were** para todas as pessoas: *if I **were** rich...*", 3),
    ("Grammar", "Gerund/Infinitive", "I enjoy ___ to music.",
     ["listen", "to listen", "listening"], 2, "Verbo: depois de **enjoy** (e like/avoid/finish) usa-se **-ing**: *enjoy **listening***. Já want/need pedem 'to + verbo'.", 2),
]


# =====================================================================
# BUILD
# =====================================================================
for sub, items in EVERYDAY.items():
    for en, pt, ipa, ex, tip, diff in items:
        add_flashcard("Everyday Phrases", sub, en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in BUSINESS:
    add_flashcard("Business English", "Meetings", en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in VOCAB:
    add_flashcard("Vocabulary", "Essential words", en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in PHRASAL:
    add_flashcard("Phrasal Verbs", "Common", en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in IDIOMS:
    add_flashcard("Idioms & Expressions", "Common idioms", en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in PRONUN:
    add_flashcard("Pronunciation", "Tricky sounds", en, pt, ipa, ex, tip, diff)

for en, pt, ipa, ex, tip, diff in CONNECTORS:
    add_flashcard("Connectors & Writing", "Linking words", en, pt, ipa, ex, tip, diff)

for frente, verso, diff in GRAMMAR_CONCEPTS:
    add_concept("Grammar", "Rules", frente, verso, diff)

for topico, sub, en, pt, ipa, ex, tip, diff in [
    ("Grammar", "Irregular verbs", f"Past & participle of '{base}'", verbs, "", "", "", 2)
    for base, verbs in [
        ("go", "went / gone"), ("do", "did / done"), ("see", "saw / seen"),
        ("take", "took / taken"), ("come", "came / come"), ("give", "gave / given"),
        ("write", "wrote / written"), ("speak", "spoke / spoken"), ("break", "broke / broken"),
        ("buy", "bought / bought"), ("think", "thought / thought"), ("bring", "brought / brought"),
        ("know", "knew / known"), ("get", "got / got(ten)"), ("make", "made / made"),
        ("eat", "ate / eaten"), ("drive", "drove / driven"), ("choose", "chose / chosen"),
    ]
]:
    add_flashcard(topico, sub, en, pt, ipa, ex, tip, diff, tags=["irregular"])

for topico, sub, enun, opts, cor, exp, diff in QUESTIONS:
    add_question(topico, sub, enun, opts, cor, exp, diff)


# =====================================================================
# EXPANSÃO DE CONTEÚDO (pacote 2)
# =====================================================================
EVERYDAY_EXTRA = {
    "Phone & Internet": [
        ("Can you hear me now?", "Você consegue me ouvir agora?", "", "", "", 1),
        ("You're breaking up.", "Está cortando / falhando (ligação).", "", "", "", 2),
        ("Let me call you back.", "Deixa eu te ligar de volta.", "", "", "", 1),
        ("The Wi-Fi is down.", "O Wi-Fi está fora do ar.", "", "", "", 1),
        ("Could you send me the link?", "Você pode me mandar o link?", "", "", "", 1),
        ("I'll text you the address.", "Eu te mando o endereço por mensagem.", "", "", "", 2),
        ("My battery is about to die.", "Minha bateria está acabando.", "", "", "", 2),
        ("Can we reschedule the call?", "Podemos remarcar a ligação?", "", "", "", 2),
    ],
    "Making plans": [
        ("Are you free this weekend?", "Você está livre neste fim de semana?", "", "", "", 1),
        ("Let's grab a coffee sometime.", "Vamos tomar um café qualquer dia.", "", "", "", 2),
        ("What time works for you?", "Que horário funciona pra você?", "", "", "", 1),
        ("I'm looking forward to it.", "Estou ansioso por isso.", "", "", "", 2),
        ("Something came up.", "Surgiu um imprevisto.", "", "", "Ótima para cancelar educadamente.", 2),
        ("Can we take a rain check?", "Podemos deixar para outra hora?", "", "", "Idiomático: adiar um convite.", 3),
        ("Count me in!", "Pode contar comigo!", "", "", "", 2),
        ("I'll let you know.", "Eu te aviso.", "", "", "", 1),
    ],
    "Hotel & Stay": [
        ("I have a reservation.", "Eu tenho uma reserva.", "", "", "", 1),
        ("What time is check-out?", "Que horas é o check-out?", "", "", "", 1),
        ("Is breakfast included?", "O café da manhã está incluído?", "", "", "", 1),
        ("Could I get a wake-up call?", "Poderia me acordar com uma ligação?", "", "", "", 2),
        ("The room is a bit noisy.", "O quarto está um pouco barulhento.", "", "", "", 2),
        ("Can I leave my bags here?", "Posso deixar minhas malas aqui?", "", "", "", 1),
    ],
    "Politeness & Apologies": [
        ("I'm so sorry, my fault.", "Me desculpa, foi culpa minha.", "", "", "", 1),
        ("No worries at all.", "Sem problema nenhum.", "", "", "", 1),
        ("Excuse me, may I get through?", "Com licença, posso passar?", "", "", "", 1),
        ("I didn't mean to.", "Eu não quis / não foi por querer.", "", "", "", 2),
        ("Would you mind helping me?", "Você se importaria de me ajudar?", "", "", "Muito educado.", 2),
        ("Thanks a million!", "Muito obrigado mesmo!", "", "", "", 1),
        ("After you.", "Você primeiro. (gentileza)", "", "", "", 2),
    ],
    "Opinions & Reactions": [
        ("That's a good point.", "Esse é um bom argumento.", "", "", "", 2),
        ("I see what you mean.", "Entendo o que você quer dizer.", "", "", "", 2),
        ("I'm not so sure about that.", "Não tenho tanta certeza disso.", "", "", "", 2),
        ("It's worth a shot.", "Vale a tentativa.", "", "", "", 2),
        ("That's fair enough.", "É justo / faz sentido.", "", "", "", 2),
        ("No way!", "De jeito nenhum! / Não acredito!", "", "", "", 1),
    ],
}

VOCAB_EXTRA = [
    ("to improve", "melhorar", "ɪmˈpruːv", "", "", 1),
    ("to increase", "aumentar", "ɪnˈkriːs", "", "verbo; substantivo: INcrease.", 2),
    ("to decrease", "diminuir", "dɪˈkriːs", "", "", 2),
    ("to allow", "permitir", "əˈlaʊ", "", "", 2),
    ("to require", "exigir / requerer", "rɪˈkwaɪər", "", "", 2),
    ("to provide", "fornecer / oferecer", "prəˈvaɪd", "", "", 2),
    ("to suggest", "sugerir", "səˈdʒest", "", "", 2),
    ("to complain", "reclamar", "kəmˈpleɪn", "", "", 2),
    ("to deserve", "merecer", "dɪˈzɜːrv", "", "", 2),
    ("to succeed", "ter sucesso / conseguir", "səkˈsiːd", "", "", 2),
    ("harsh", "duro / severo", "hɑːrʃ", "", "", 3),
    ("smooth", "suave / tranquilo", "smuːð", "", "", 2),
    ("tough", "difícil / durão", "tʌf", "", "", 2),
    ("fair", "justo", "feər", "", "", 1),
    ("wealthy", "rico / próspero", "ˈwelθi", "", "", 2),
    ("accurate", "preciso / exato", "ˈækjərət", "", "", 3),
    ("meaningful", "significativo", "", "", "", 3),
    ("aware", "ciente / consciente", "əˈweər", "Are you aware of the risks?", "", 2),
    ("in charge of", "responsável por", "", "She's in charge of sales.", "", 2),
    ("on purpose", "de propósito", "", "", "≠ by accident.", 2),
    ("at least", "pelo menos", "", "", "", 1),
    ("as soon as possible", "o mais rápido possível", "", "", "sigla: ASAP.", 2),
    ("regarding", "a respeito de / sobre", "", "Regarding your email...", "", 3),
    ("throughout", "ao longo de / por todo", "θruːˈaʊt", "", "", 3),
]

PHRASAL_EXTRA = [
    ("set up", "montar / configurar", "", "Let's set up a meeting.", "", 2),
    ("break down", "quebrar (parar de funcionar)", "", "My car broke down.", "", 2),
    ("check in", "fazer check-in", "", "", "", 1),
    ("check out", "sair (hotel) / dar uma olhada", "", "Check out this article!", "", 2),
    ("call off", "cancelar", "", "They called off the trip.", "", 2),
    ("catch up", "colocar o papo em dia / alcançar", "", "Let's catch up soon.", "", 2),
    ("hang out", "sair / passar o tempo", "", "We hung out yesterday.", "", 2),
    ("hang on", "esperar (segura aí)", "", "Hang on a second.", "", 1),
    ("point out", "apontar / destacar", "", "She pointed out a mistake.", "", 3),
    ("sort out", "resolver / organizar", "", "I'll sort it out.", "", 2),
    ("take off", "decolar / tirar (roupa)", "", "The plane took off.", "", 2),
    ("come across", "topar com / dar a impressão", "", "I came across an old photo.", "", 3),
]

IDIOMS_EXTRA = [
    ("Under the weather.", "Meio adoentado / indisposto.", "", "", "", 3),
    ("On the same page.", "Alinhados / de acordo.", "", "", "", 2),
    ("The ball is in your court.", "A decisão / vez é sua.", "", "", "", 3),
    ("Cut to the chase.", "Ir direto ao ponto.", "", "", "", 3),
    ("Get the hang of it.", "Pegar o jeito.", "", "", "", 2),
    ("A blessing in disguise.", "Um mal que veio para o bem.", "", "", "", 3),
    ("Back to square one.", "De volta à estaca zero.", "", "", "", 3),
    ("Beat around the bush.", "Enrolar / não ir direto ao ponto.", "", "", "", 3),
    ("Call it a day.", "Encerrar por hoje.", "", "", "", 2),
    ("Piece of cake.", "Moleza.", "", "", "", 2),
]

BUSINESS_EXTRA = [
    ("Let's align on this.", "Vamos nos alinhar sobre isso.", "", "", "", 2),
    ("Can you keep me in the loop?", "Pode me manter informado?", "", "", "", 3),
    ("Let's take this offline.", "Vamos tratar disso depois/à parte.", "", "", "Jargão de reunião.", 3),
    ("What's the deadline?", "Qual é o prazo?", "", "", "", 1),
    ("I'll follow up with you.", "Eu faço o acompanhamento com você.", "", "", "", 2),
    ("Let's touch base tomorrow.", "Vamos conversar/alinhar amanhã.", "", "", "", 3),
    ("Can we push it to next week?", "Podemos empurrar para a semana que vem?", "", "", "", 2),
    ("I'm swamped right now.", "Estou atolado de trabalho agora.", "", "", "", 3),
    ("Let's move forward with it.", "Vamos seguir em frente com isso.", "", "", "", 2),
    ("That works for me.", "Por mim funciona.", "", "", "", 1),
    ("Let me loop in the team.", "Deixa eu incluir a equipe.", "", "", "", 3),
    ("Just a heads-up:", "Só um aviso / adiantando:", "", "", "", 3),
]

PRONUN_EXTRA = [
    ("thought / taught", "pensamento / ensinou", "θɔːt / tɔːt", "", "/θ/ vs /t/.", 3),
    ("cat / cut", "gato / cortar", "kæt / kʌt", "", "/æ/ vs /ʌ/.", 2),
    ("bad / bed", "ruim / cama", "bæd / bed", "", "/æ/ vs /e/.", 2),
    ("full / fool", "cheio / bobo", "fʊl / fuːl", "", "/ʊ/ curto vs /uː/ longo.", 2),
    ("vowel / bowel", "vogal / intestino", "ˈvaʊəl / ˈbaʊəl", "", "cuidado com /v/ vs /b/.", 3),
    ("island", "ilha", "ˈaɪlənd", "", "o 's' é mudo: AI-land.", 2),
    ("receipt", "recibo", "rɪˈsiːt", "", "o 'p' é mudo.", 3),
    ("although", "embora", "ɔːlˈðoʊ", "", "termina com som /oʊ/.", 2),
    ("focus", "foco / focar", "ˈfoʊkəs", "", "FO-cus, não 'fâquis'.", 1),
    ("develop", "desenvolver", "dɪˈveləp", "", "tônica no VE: de-VE-lop.", 2),
    ("determine", "determinar", "dɪˈtɜːrmɪn", "", "termina com /ɪn/, não 'main'.", 3),
    ("vegetable", "vegetal / legume", "ˈvedʒtəbl", "", "3 sílabas: VEJ-ta-bl.", 2),
]

CONNECTORS_EXTRA = [
    ("Therefore, ...", "Portanto, ...", "", "", "", 2),
    ("Otherwise, ...", "Caso contrário, ...", "", "", "", 2),
    ("Meanwhile, ...", "Enquanto isso, ...", "", "", "", 2),
    ("As a matter of fact, ...", "Na verdade / aliás, ...", "", "", "", 3),
    ("First of all, ...", "Antes de tudo, ...", "", "", "", 1),
    ("On top of that, ...", "Além do mais, ...", "", "", "", 2),
    ("In conclusion, ...", "Concluindo, ...", "", "", "", 2),
    ("Even though ...", "Mesmo que / apesar de ...", "", "Even though it's hard, I'll try.", "", 2),
]

GRAMMAR_EXTRA = [
    ("used to + verbo",
     "Hábito ou estado no passado que não acontece mais.\n\n"
     "> *I **used to** smoke. She **used to** live here.*\n\n"
     "Negativa/pergunta: *didn't use to / did you use to*.", 2),
    ("There is vs There are",
     "**There is** + singular/incontável: *There is a book / some milk*.\n\n"
     "**There are** + plural: *There are two cars*.", 1),
    ("Present perfect: for vs since",
     "**for** + período (*for 3 years, for a while*).\n\n"
     "**since** + ponto no tempo (*since 2020, since Monday*).", 2),
    ("Countable vs uncountable",
     "Contáveis têm plural (*books, apples*). Incontáveis não (*water, information, advice, money*).\n\n"
     "Com incontáveis use *some, much, a little*.", 2),
    ("Word order (adjetivo + substantivo)",
     "Em inglês o adjetivo vem **antes** do substantivo: *a **red car*** (não 'a car red').\n\n"
     "Ordem: opinião → tamanho → idade → cor → origem.", 2),
    ("Question tags",
     "Frase afirmativa → tag negativa: *You're coming, **aren't you**?*\n\n"
     "Frase negativa → tag afirmativa: *He isn't here, **is he**?*", 3),
    ("Modais: can / could / should / must",
     "**can** = habilidade/permissão; **could** = passado/educado; "
     "**should** = conselho; **must** = obrigação forte.\n\n"
     "> *You **should** rest. You **must** wear a seatbelt.*", 2),
    ("Comparações: as ... as",
     "Igualdade: *as tall **as** you*. Negativa: *not as expensive as*.", 2),
]

QUESTIONS_EXTRA = [
    ("Grammar", "Prepositions", "I'm interested ___ learning Japanese.",
     ["on", "in", "at"], 1, "Preposição fixa: 'be **interested in** + **-ing**': *interested in **learning***.", 2),
    ("Grammar", "Prepositions", "She's married ___ a doctor.",
     ["with", "to", "at"], 1, "Preposição fixa: 'be **married to** somebody' (nunca 'married with').", 2),
    ("Grammar", "Prepositions", "We arrived ___ the airport late.",
     ["at", "to", "in"], 0, "Preposição: **arrive at** (lugar específico: at the airport); **arrive in** (cidade/país). Nunca 'arrive to'.", 3),
    ("Grammar", "Prepositions", "I'll see you ___ Monday.",
     ["in", "at", "on"], 2, "Preposição de tempo: **on** para dias/datas (on Monday); **at** para horas; **in** para meses/anos.", 1),
    ("Grammar", "Prepositions", "The meeting is ___ 3 p.m.",
     ["at", "on", "in"], 0, "Preposição de tempo: **at** para horas (at 3 p.m.); **on** para dias; **in** para meses/anos.", 1),
    ("Grammar", "Articles", "She is ___ honest person.",
     ["a", "an", "the"], 1, "Artigo: vale o **som**, não a letra. 'honest' tem **h mudo** (começa com som de vogal) → **an** honest person.", 3),
    ("Grammar", "Tenses", "Look! It ___ .",
     ["rains", "is raining", "rained"], 1, "Verbo: 'Look!' mostra algo acontecendo **agora** → **Present Continuous** (be + verbo-ing): *is raining*.", 2),
    ("Grammar", "Tenses", "By the time we arrived, the movie ___ .",
     ["started", "has started", "had started"], 2, "Verbo: a ação que aconteceu **antes** de outra no passado vai para o **Past Perfect** (had + particípio): *had started*. 'started' seria ao mesmo tempo.", 3),
    ("Grammar", "Tenses", "I ___ him since last year.",
     ["didn't see", "haven't seen", "don't see"], 1, "Verbo: **since** (desde + um ponto no tempo) pede **Present Perfect**: *haven't seen*. Passado simples não combina com 'since'.", 2),
    ("Grammar", "Conditionals", "If you heat ice, it ___ .",
     ["melts", "will melt", "would melt"], 0, "Verbo: para fatos/verdades gerais usa-se o **Zero Conditional** — 'if + presente, presente': *if you heat ice, it **melts***.", 2),
    ("Grammar", "Modals", "You ___ smoke here. It's forbidden.",
     ["mustn't", "don't have to", "shouldn't"], 0, "Verbo modal: **mustn't** = proibição (não pode). 'don't have to' seria 'não é obrigatório' — sentido diferente.", 3),
    ("Grammar", "Modals", "It's optional — you ___ come if you don't want to.",
     ["mustn't", "don't have to", "can't"], 1, "Verbo modal: **don't have to** = não é obrigatório (opcional). 'mustn't' seria proibido.", 3),
    ("Grammar", "Quantifiers", "How ___ money do you have?",
     ["many", "much", "some"], 1, "Substantivo: **money** é **incontável** (não tem plural), então usa-se **much**. 'many' é só para contáveis no plural.", 2),
    ("Grammar", "Quantifiers", "There are too ___ people here.",
     ["much", "many", "few"], 1, "Substantivo: **people** é o plural de 'person' = **contável**, então **many**. 'much' é só para incontáveis.", 2),
    ("Grammar", "Comparatives", "This test is ___ than the last one.",
     ["difficult", "more difficult", "most difficult"], 1, "Comparativo: adjetivos **longos** (2+ sílabas) usam **more + adjetivo**: *more difficult*. Curtos levam **-er**.", 2),
    ("Grammar", "Comparatives", "She runs ___ than me.",
     ["fast", "faster", "fastest"], 1, "Comparativo: adjetivos/advérbios **curtos** levam **-er**: fast → **faster** (+ than).", 1),
    ("Grammar", "Superlatives", "It's the ___ day of my life!",
     ["good", "better", "best"], 2, "Superlativo: **good** é irregular → good / better / **best** (the best).", 2),
    ("Grammar", "Gerund/Infinitive", "I need ___ a new phone.",
     ["buy", "to buy", "buying"], 1, "Verbo: depois de **need/want/decide** vem **to + verbo** (infinitivo): *need **to buy***.", 2),
    ("Grammar", "Gerund/Infinitive", "She's good at ___ problems.",
     ["solve", "to solve", "solving"], 2, "Verbo: depois de **preposição** (at, in, of, about...) o verbo vira **-ing** (gerúndio): *good at **solving***.", 2),
    ("Grammar", "Question tags", "You're coming, ___ ?",
     ["are you", "aren't you", "don't you"], 1, "Verbo: frase **afirmativa** leva **question tag negativa**, repetindo o auxiliar: *You're coming, **aren't you?***", 3),
    ("Grammar", "used to", "I ___ play soccer when I was a kid.",
     ["use to", "used to", "am used to"], 1, "Verbo: **used to + verbo** = hábito no passado que não acontece mais: *I **used to** play*. (Com 'did' vira 'use to'.)", 2),
    ("Vocabulary", "Word choice", "Can you ___ me a favor?",
     ["do", "make", "take"], 0, "Colocação: **do** para tarefas/atividades → *do a favor, do the dishes*. (make = criar/produzir.)", 2),
    ("Vocabulary", "Word choice", "I need to ___ a decision.",
     ["do", "make", "take"], 1, "Colocação: **make** para criar/produzir → *make a decision, make dinner*. (do = tarefas.)", 2),
    ("Vocabulary", "Word choice", "He ___ a lot of money as an engineer.",
     ["wins", "earns", "gains"], 1, "Vocabulário: **earn** = ganhar (dinheiro trabalhando). 'win' = ganhar competição/prêmio; 'gain' = adquirir (peso, experiência).", 3),
    ("Vocabulary", "Word choice", "Please ___ the light off.",
     ["turn", "close", "shut"], 0, "'turn off the light'.", 1),
    ("Vocabulary", "False friends", "'Pretend' significa:",
     ["pretender", "fingir", "prender"], 1, "'pretend' = fingir; 'pretender' = intend.", 2),
    ("Vocabulary", "False friends", "'Actually' NÃO significa:",
     ["na verdade", "de fato", "atualmente"], 2, "'actually' = na verdade; 'atualmente' = currently.", 2),
    ("Vocabulary", "Word choice", "This information ___ very useful.",
     ["are", "is", "were"], 1, "Substantivo: **information** é **incontável** → verbo no **singular** (*is*) e sem 'a/an' nem plural.", 3),
    ("Vocabulary", "Synonyms", "A synonym for 'huge' is:",
     ["tiny", "enormous", "narrow"], 1, "'huge' = enorme = enormous.", 2),
    ("Phrasal Verbs", "Meaning", "'The car broke down' means it ___ .",
     ["was stolen", "stopped working", "got faster"], 1, "'break down' = quebrar/parar de funcionar.", 2),
    ("Phrasal Verbs", "Meaning", "Let's ___ the meeting; nobody can come. (cancelar)",
     ["call off", "call on", "call up"], 0, "'call off' = cancelar.", 2),
    ("Phrasal Verbs", "Meaning", "I need to ___ on my emails. (colocar em dia)",
     ["catch up", "catch on", "catch out"], 0, "'catch up' = pôr em dia.", 2),
    ("Phrasal Verbs", "Meaning", "Please ___ your shoes before entering. (tirar)",
     ["take off", "take up", "take in"], 0, "'take off' = tirar (roupa/calçado).", 2),
    ("Idioms & Expressions", "Meaning", "'It cost an arm and a leg' means it was very ___ .",
     ["cheap", "expensive", "easy"], 1, "'cost an arm and a leg' = caríssimo.", 2),
    ("Idioms & Expressions", "Meaning", "'I'm feeling under the weather' means I feel ___ .",
     ["great", "sick", "angry"], 1, "'under the weather' = indisposto.", 3),
    ("Idioms & Expressions", "Meaning", "'Let's cut to the chase' means let's ___ .",
     ["get to the point", "take a break", "go home"], 0, "'cut to the chase' = ir direto ao ponto.", 3),
    ("Pronunciation", "Silent letters", "Which letter is silent in 'island'?",
     ["l", "s", "d"], 1, "O 's' é mudo: /ˈaɪlənd/.", 3),
    ("Pronunciation", "Sounds", "Which word has the /θ/ sound (as in 'think')?",
     ["this", "three", "the"], 1, "'three' tem /θ/; 'this'/'the' têm /ð/.", 3),
    ("Pronunciation", "Stress", "Where is the stress in 'deVElop'?",
     ["1st syllable", "2nd syllable", "3rd syllable"], 1, "de-VE-lop: tônica na 2ª.", 2),
    ("Everyday Phrases", "Usage", "Someone says 'Thank you!'. A natural reply is:",
     ["You're welcome!", "Please.", "Yes, I do."], 0, "Resposta natural a agradecimento.", 1),
    ("Everyday Phrases", "Usage", "To politely decline food, you can say:",
     ["No!", "I'm good, thanks.", "I don't want."], 1, "Educado e natural.", 2),
    ("Connectors & Writing", "Usage", "___ the rain, we went out.",
     ["Despite", "Although", "Because"], 0, "'Despite' + substantivo ('the rain').", 3),
    ("Connectors & Writing", "Usage", "___ it was raining, we went out.",
     ["Despite", "Although", "In spite"], 1, "'Although' + oração (sujeito+verbo).", 3),
    ("Grammar", "Tenses", "While I ___ , the phone rang.",
     ["cooked", "was cooking", "cook"], 1, "Ação em progresso interrompida → past continuous.", 2),
    ("Business English", "Meaning", "'Let's take this offline' means let's discuss it ___ .",
     ["later/separately", "on the internet", "louder"], 0, "Jargão: tratar fora da reunião.", 3),
]

for sub, items in EVERYDAY_EXTRA.items():
    for en, pt, ipa, ex, tip, diff in items:
        add_flashcard("Everyday Phrases", sub, en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in VOCAB_EXTRA:
    add_flashcard("Vocabulary", "Essential words", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in PHRASAL_EXTRA:
    add_flashcard("Phrasal Verbs", "Common", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in IDIOMS_EXTRA:
    add_flashcard("Idioms & Expressions", "Common idioms", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in BUSINESS_EXTRA:
    add_flashcard("Business English", "Meetings", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in PRONUN_EXTRA:
    add_flashcard("Pronunciation", "Tricky sounds", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in CONNECTORS_EXTRA:
    add_flashcard("Connectors & Writing", "Linking words", en, pt, ipa, ex, tip, diff)
for frente, verso, diff in GRAMMAR_EXTRA:
    add_concept("Grammar", "Rules", frente, verso, diff)
for topico, sub, enun, opts, cor, exp, diff in QUESTIONS_EXTRA:
    add_question(topico, sub, enun, opts, cor, exp, diff)

# =====================================================================
# EXPANSÃO DE CONTEÚDO (pacote 3) — NÍVEL AVANÇADO / FLUÊNCIA
# =====================================================================
FLUENCY = {
    "Discourse markers": [
        ("The thing is, ...", "A questão é que... / Acontece que...", "", "The thing is, I already made plans.", "Ganha tempo e introduz o ponto.", 3),
        ("I mean, ...", "Quer dizer, ... / Ou seja, ...", "", "I mean, it's not a big deal.", "Reformula/explica o que você disse.", 2),
        ("You know what I mean?", "Você entende o que eu quero dizer?", "", "", "Checa se o outro acompanhou.", 2),
        ("Now that you mention it, ...", "Agora que você falou / mencionou, ...", "", "", "", 3),
        ("Speaking of which, ...", "Por falar nisso, ...", "", "", "Emenda um assunto relacionado.", 3),
        ("That reminds me, ...", "Isso me lembra que...", "", "", "", 2),
        ("Come to think of it, ...", "Pensando bem, ...", "", "", "", 3),
        ("As I was saying, ...", "Como eu estava dizendo, ...", "", "", "Retoma depois de uma interrupção.", 2),
        ("Anyway, ...", "Enfim, ... / De qualquer forma, ...", "", "", "Fecha um assunto e segue.", 2),
        ("Let me put it this way.", "Deixa eu colocar assim / de outro jeito.", "", "", "", 3),
        ("How can I put this?", "Como é que eu digo isso?", "", "", "Ganha tempo pra achar as palavras.", 3),
        ("Where was I?", "Onde eu estava? (voltando à história)", "", "", "", 2),
    ],
    "Reacting naturally": [
        ("No way!", "Não acredito! / De jeito nenhum!", "", "", "", 1),
        ("You're kidding!", "Você está brincando! / Tá de sacanagem!", "", "", "", 2),
        ("Tell me about it!", "Nem me fale!", "", "", "Concorda com uma queixa.", 3),
        ("You can say that again!", "Isso mesmo! / Pode falar de novo!", "", "", "Concordância enfática.", 3),
        ("I know, right?", "Né?! / Pois é!", "", "", "Super comum e natural.", 2),
        ("Oh, come on!", "Ah, qual é! / Fala sério!", "", "", "", 2),
        ("No wonder!", "Com razão! / Não é à toa!", "", "No wonder you're tired!", "", 3),
        ("Good for you!", "Que bom pra você! / Mandou bem!", "", "", "", 2),
        ("That's a shame.", "Que pena.", "", "", "", 2),
        ("Fair enough.", "Justo. / Faz sentido.", "", "", "Aceita o argumento do outro.", 3),
        ("It happens.", "Acontece.", "", "", "", 1),
        ("What a relief!", "Que alívio!", "", "", "", 2),
    ],
    "Softening & diplomacy": [
        ("I was wondering if you could ...", "Eu queria saber se você poderia... (pedido educado)", "", "I was wondering if you could help me.", "Jeito muito educado de pedir.", 3),
        ("Would it be possible to ...?", "Seria possível...?", "", "", "", 3),
        ("I'm afraid I can't.", "Infelizmente não vou poder.", "", "", "'I'm afraid' suaviza uma recusa.", 2),
        ("To be fair, ...", "Para ser justo, ...", "", "", "", 3),
        ("Correct me if I'm wrong, but ...", "Me corrija se eu estiver errado, mas...", "", "", "", 3),
        ("With all due respect, ...", "Com todo o respeito, ...", "", "", "Antes de discordar educadamente.", 3),
        ("I'd rather not, if that's okay.", "Prefiro não, se não tem problema.", "", "", "", 3),
        ("It's not really my thing.", "Não é bem a minha praia.", "", "", "", 3),
        ("I guess so.", "Acho que sim. (sem muita certeza)", "", "", "", 2),
        ("Not that I know of.", "Que eu saiba, não.", "", "", "", 3),
        ("kind of / sort of", "meio que / tipo (suaviza)", "", "It's kind of expensive.", "Deixa a fala menos categórica.", 2),
    ],
    "Agreeing & disagreeing": [
        ("That's exactly my point.", "É exatamente o que eu digo.", "", "", "", 3),
        ("I see your point, but ...", "Entendo seu ponto, mas...", "", "", "Discorda com respeito.", 3),
        ("I'm not so sure about that.", "Não tenho tanta certeza disso.", "", "", "Discordância suave.", 2),
        ("I beg to differ.", "Permita-me discordar. (formal)", "", "", "", 3),
        ("You have a point.", "Você tem razão / tem um ponto.", "", "", "", 2),
        ("I couldn't agree more.", "Concordo plenamente.", "", "", "", 3),
        ("Absolutely!", "Com certeza! / Absolutamente!", "", "", "", 1),
        ("Not necessarily.", "Não necessariamente.", "", "", "", 2),
        ("It depends.", "Depende.", "", "", "", 1),
        ("Well, it's complicated.", "Bem, é complicado.", "", "", "", 2),
    ],
    "Storytelling": [
        ("Long story short, ...", "Resumindo a história, ...", "", "", "", 3),
        ("So basically, ...", "Então, basicamente, ...", "", "", "", 2),
        ("The next thing I knew, ...", "Quando eu vi, ... / Do nada, ...", "", "", "", 3),
        ("Out of nowhere, ...", "Do nada, ...", "", "", "", 3),
        ("To make matters worse, ...", "Para piorar, ...", "", "", "", 3),
        ("At the end of the day, ...", "No fim das contas, ...", "", "", "Idiomático, muito usado.", 3),
        ("Believe it or not, ...", "Acredite ou não, ...", "", "", "", 2),
        ("As it turns out, ...", "Acontece que... / No fim das contas...", "", "", "", 3),
        ("One thing led to another.", "Uma coisa levou a outra.", "", "", "", 3),
    ],
    "Opinions & argument": [
        ("From my perspective, ...", "Do meu ponto de vista, ...", "", "", "", 3),
        ("If you ask me, ...", "Se quer minha opinião, ...", "", "", "", 3),
        ("The way I see it, ...", "Do jeito que eu vejo, ...", "", "", "", 3),
        ("There's no denying that ...", "Não dá pra negar que...", "", "", "", 3),
        ("It goes without saying that ...", "Nem preciso dizer que...", "", "", "", 3),
        ("That being said, ...", "Dito isso, ...", "", "", "Introduz uma ressalva.", 3),
        ("On the one hand ... on the other hand ...", "Por um lado... por outro lado...", "", "", "", 3),
        ("Let's agree to disagree.", "Vamos concordar em discordar.", "", "", "", 3),
    ],
    "Connected speech (casual)": [
        ("gonna (going to)", "vou / vai (fala casual)", "ˈɡɔːnə", "I'm gonna call you.", "Só na fala/informal, não em texto formal.", 2),
        ("wanna (want to)", "quero / quer (fala casual)", "ˈwɒnə", "Do you wanna go?", "Informal.", 2),
        ("gotta (have got to)", "tenho que (fala casual)", "ˈɡɒtə", "I gotta go.", "Informal.", 2),
        ("gimme (give me)", "me dá (fala casual)", "ˈɡɪmi", "Gimme a second.", "Informal.", 2),
        ("lemme (let me)", "deixa eu (fala casual)", "ˈlemi", "Lemme see.", "Informal.", 2),
        ("kinda (kind of)", "meio que (fala casual)", "ˈkaɪndə", "I'm kinda tired.", "", 2),
        ("dunno (don't know)", "sei lá / não sei (casual)", "dəˈnoʊ", "I dunno.", "", 2),
        ("What's up? / 'Sup?", "E aí? / Beleza?", "", "", "Cumprimento informal.", 1),
        ("How's it going?", "Como vão as coisas?", "", "", "", 1),
        ("'cause (because)", "porque (fala casual)", "kəz", "", "", 2),
    ],
}

IDIOMS_ADV = [
    ("Get cold feet", "Amarelar / ficar com medo na hora", "", "He got cold feet before the wedding.", "", 3),
    ("Call the shots", "Dar as cartas / mandar", "", "", "", 3),
    ("Cut corners", "Fazer nas coxas / economizar de forma ruim", "", "", "", 3),
    ("Get the ball rolling", "Dar o pontapé inicial", "", "", "", 3),
    ("Wrap your head around it", "Conseguir assimilar / entender", "", "I can't wrap my head around it.", "", 3),
    ("On the fence", "Em cima do muro / indeciso", "", "I'm on the fence about it.", "", 3),
    ("Bite off more than you can chew", "Abraçar o mundo / assumir demais", "", "", "", 3),
    ("Play it by ear", "Ver como as coisas vão / improvisar", "", "Let's play it by ear.", "", 3),
    ("It's a no-brainer.", "É óbvio / decisão fácil.", "", "", "", 3),
    ("The bottom line is ...", "O ponto principal é ...", "", "", "", 3),
    ("Hit the sack", "Ir dormir / cair na cama", "", "", "", 2),
    ("Pull someone's leg", "Zoar / brincar com alguém", "", "I'm just pulling your leg.", "", 3),
    ("Fly under the radar", "Passar despercebido", "", "", "", 3),
    ("Rings a bell", "Soa familiar", "", "The name rings a bell.", "", 3),
    ("Give it a shot", "Dar uma chance / tentar", "", "Just give it a shot!", "", 2),
]

PHRASAL_ADV = [
    ("put up with", "tolerar / aguentar", "", "I can't put up with the noise.", "", 3),
    ("get away with", "se safar de (algo errado)", "", "He got away with it.", "", 3),
    ("come down to", "resumir-se a / depender de", "", "It comes down to money.", "", 3),
    ("look into", "investigar / apurar", "", "I'll look into it.", "", 2),
    ("back (someone) up", "apoiar / dar respaldo", "", "I'll back you up.", "", 2),
    ("make up for", "compensar", "", "Let me make up for it.", "", 3),
    ("run into", "encontrar por acaso / esbarrar em", "", "I ran into an old friend.", "", 2),
    ("get by", "se virar / dar um jeito", "", "I can get by with basic English.", "", 3),
    ("pull off", "conseguir (algo difícil)", "", "She pulled it off!", "", 3),
    ("stand out", "se destacar", "", "Your CV needs to stand out.", "", 2),
    ("wear off", "passar (efeito)", "", "The painkiller wore off.", "", 3),
    ("mess up", "estragar / errar feio", "", "Sorry, I messed up.", "", 2),
    ("wind up (doing)", "acabar (fazendo)", "", "We wound up staying home.", "", 3),
    ("cut back on", "reduzir / cortar", "", "I need to cut back on coffee.", "", 3),
]

VOCAB_ADV = [
    ("thorough", "minucioso / completo", "ˈθɜːroʊ", "a thorough review", "", 3),
    ("blunt", "direto / sem rodeios", "blʌnt", "to be blunt...", "", 3),
    ("subtle", "sutil", "ˈsʌtl", "", "o 'b' é mudo!", 3),
    ("reluctant", "relutante / sem vontade", "rɪˈlʌktənt", "", "", 3),
    ("eager", "ávido / muito a fim (positivo)", "ˈiːɡər", "eager to learn", "", 3),
    ("overwhelmed", "sobrecarregado / assoberbado", "ˌoʊvərˈwelmd", "", "", 3),
    ("resilient", "resiliente", "rɪˈzɪliənt", "", "", 3),
    ("compelling", "convincente / cativante", "kəmˈpelɪŋ", "a compelling argument", "", 3),
    ("feasible", "viável / factível", "ˈfiːzəbl", "", "", 3),
    ("cumbersome", "trabalhoso / pesado", "ˈkʌmbərsəm", "", "", 3),
    ("arguably", "possivelmente / pode-se dizer que", "ˈɑːrɡjuəbli", "arguably the best", "", 3),
    ("eventually", "no fim / com o tempo", "ɪˈventʃuəli", "", "NÃO é 'eventualmente' (=occasionally).", 3),
    ("thrive", "prosperar / se dar muito bem", "θraɪv", "", "", 3),
    ("hassle", "transtorno / incômodo", "ˈhæsl", "It's a hassle.", "", 3),
    ("handy", "útil / à mão / jeitoso", "ˈhændi", "That comes in handy.", "", 2),
    ("cope with", "lidar / dar conta de", "koʊp", "How do you cope with stress?", "", 3),
    ("straightforward", "simples e direto", "", "", "", 2),
    ("insightful", "perspicaz / esclarecedor", "", "", "", 3),
    ("worthwhile", "que vale a pena", "", "It was worthwhile.", "", 3),
    ("keen on", "muito a fim de / entusiasmado com", "", "I'm keen on learning.", "", 3),
]

BUSINESS_ADV = [
    ("Let's touch base early next week.", "Vamos nos alinhar no começo da semana.", "", "", "", 3),
    ("I'll circle back with the details.", "Eu retorno com os detalhes.", "", "", "", 3),
    ("Can we take this offline?", "Podemos tratar disso à parte / depois?", "", "", "", 3),
    ("Let's park this for now.", "Vamos deixar isso de lado por ora.", "", "", "", 3),
    ("What's the ballpark figure?", "Qual o valor aproximado?", "", "", "", 3),
    ("Let's not reinvent the wheel.", "Não vamos reinventar a roda.", "", "", "", 3),
    ("I'll take ownership of this.", "Eu assumo a responsabilidade disso.", "", "", "", 3),
    ("Let's manage expectations.", "Vamos alinhar as expectativas.", "", "", "", 3),
    ("That's a game changer.", "Isso muda o jogo.", "", "", "", 2),
    ("Let's move the needle on this.", "Vamos fazer diferença nisso de fato.", "", "", "", 3),
    ("Can you ballpark it?", "Você consegue estimar por alto?", "", "", "", 3),
    ("Let's regroup after lunch.", "Vamos nos reunir de novo depois do almoço.", "", "", "", 3),
]

GRAMMAR_ADV = [
    ("used to vs be used to vs get used to",
     "**used to + verbo** = hábito passado que acabou (*I used to run*).\n\n"
     "**be used to + -ing** = estar acostumado (*I'm used to running*).\n\n"
     "**get used to + -ing** = se acostumando (*I'm getting used to running*).", 3),
    ("Reported speech (discurso indireto)",
     "O verbo recua um tempo: present→past, will→would, can→could.\n\n"
     "> *\"I **am** busy\" → She said she **was** busy.*", 3),
    ("wish / if only",
     "Desejo/arrependimento no presente → **past**: *I wish I **knew**.*\n\n"
     "No passado → **past perfect**: *I wish I **had known**.*", 3),
    ("Mixed conditional",
     "Passado hipotético → presente: *If I **had saved** money, I **would be** rich now.*", 3),
    ("Modals of deduction",
     "**must** (certeza), **can't** (impossível), **might/could** (talvez): "
     "*He **must be** home; the lights are on.*", 3),
    ("would (hábito no passado)",
     "**would + verbo** para hábitos passados (como 'used to'): "
     "*When I was a kid, we **would** spend summers at the beach.*", 3),
]

QUESTIONS_ADV = [
    ("Fluency & Speaking", "Softening", "Qual soa MAIS educado para um pedido?",
     ["Give me your report.", "I was wondering if you could send me the report.", "Send the report now."], 1,
     "'I was wondering if you could...' é a forma mais educada e natural de pedir.", 3),
    ("Fluency & Speaking", "Reacting", "Seu amigo diz: 'The traffic was a nightmare!' Resposta natural de empatia:",
     ["Tell me about it!", "Good for you!", "No wonder!"], 0,
     "'Tell me about it!' concorda com a queixa ('nem me fale!').", 3),
    ("Grammar", "used to / be used to", "I ___ getting up early now — it doesn't bother me anymore.",
     ["used to", "am used to", "would"], 1,
     "Verbo: **be used to + -ing** = estar acostumado (estado atual). 'used to' seria hábito que acabou.", 3),
    ("Grammar", "Reported speech", "\"I will help you.\" → She said she ___ help me.",
     ["will", "would", "helps"], 1,
     "No discurso indireto, **will → would**.", 3),
    ("Grammar", "wish", "I wish I ___ more time to study.",
     ["have", "had", "will have"], 1,
     "Verbo: após **wish** (desejo no presente) usa-se o **past** (had), não o presente.", 3),
    ("Grammar", "wish (past)", "I wish I ___ harder for the exam last year.",
     ["studied", "had studied", "study"], 1,
     "Verbo: arrependimento sobre o **passado** → **past perfect** (had studied).", 3),
    ("Grammar", "Mixed conditional", "If she ___ the job, she'd be living in London now.",
     ["took", "had taken", "takes"], 1,
     "Verbo: condição no passado + resultado no presente → **if + past perfect** (had taken).", 3),
    ("Grammar", "Modals of deduction", "The lights are off. They ___ be home.",
     ["must", "can't", "should"], 1,
     "Verbo modal: evidência de que é impossível → **can't** (dedução negativa).", 3),
    ("Grammar", "Inversion", "Never ___ such a beautiful place.",
     ["I have seen", "have I seen", "I saw"], 1,
     "Com 'Never' no início, inverte-se: **have I seen** (auxiliar antes do sujeito).", 3),
    ("Idioms & Expressions", "Meaning", "'It's a no-brainer' means the decision is ___.",
     ["very hard", "obvious/easy", "risky"], 1, "'no-brainer' = decisão óbvia, fácil.", 3),
    ("Idioms & Expressions", "Meaning", "'He got cold feet' means he ___.",
     ["got sick", "got nervous and hesitated", "got angry"], 1, "'get cold feet' = amarelar/hesitar por medo.", 3),
    ("Phrasal Verbs", "Meaning", "'I can't put up with it' means I can't ___ it.",
     ["understand", "tolerate", "afford"], 1, "'put up with' = tolerar/aguentar.", 3),
    ("Phrasal Verbs", "Meaning", "'She pulled it off' means she ___.",
     ["failed", "succeeded at something hard", "gave up"], 1, "'pull off' = conseguir algo difícil.", 3),
    ("Vocabulary", "False friends", "'Eventually' significa:",
     ["eventualmente/às vezes", "no fim / com o tempo", "possivelmente"], 1,
     "'eventually' = no fim/com o tempo (não 'eventualmente' = occasionally).", 3),
    ("Vocabulary", "Nuance", "A '**blunt**' person is someone who is ___.",
     ["very polite", "direct/frank", "shy"], 1, "'blunt' = direto, sem rodeios (às vezes rude).", 3),
]

for sub, items in FLUENCY.items():
    for en, pt, ipa, ex, tip, diff in items:
        add_flashcard("Fluency & Speaking", sub, en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in IDIOMS_ADV:
    add_flashcard("Idioms & Expressions", "Advanced", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in PHRASAL_ADV:
    add_flashcard("Phrasal Verbs", "Advanced", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in VOCAB_ADV:
    add_flashcard("Vocabulary", "Advanced", en, pt, ipa, ex, tip, diff)
for en, pt, ipa, ex, tip, diff in BUSINESS_ADV:
    add_flashcard("Business English", "Advanced", en, pt, ipa, ex, tip, diff)
for frente, verso, diff in GRAMMAR_ADV:
    add_concept("Grammar", "Advanced", frente, verso, diff)
for topico, sub, enun, opts, cor, exp, diff in QUESTIONS_ADV:
    add_question(topico, sub, enun, opts, cor, exp, diff)

out = {"cards": cards}
path = os.path.join(os.path.dirname(__file__), "seed_cards.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

from collections import Counter
print(f"OK: {len(cards)} cards ->", path)
print("tipos:", dict(Counter(c["tipo"] for c in cards)))
print("topicos:", dict(Counter(c["topico"] for c in cards)))
