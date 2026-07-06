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
     "Com tempo definido ('yesterday') use o Past Simple: *saw*.", 2),
    ("Grammar", "Present Perfect", "I ___ in São Paulo for ten years (and still live here).",
     ["live", "lived", "have lived"], 2,
     "Ação que começou no passado e continua: Present Perfect com 'for'.", 3),
    ("Grammar", "Prepositions", "She's really good ___ playing the guitar.",
     ["in", "at", "on"], 1, "'good at + -ing' é a colocação correta.", 2),
    ("Grammar", "Articles", "I need to buy ___ umbrella.",
     ["a", "an", "the"], 1, "'an' antes de som de vogal (umbrella começa com /ʌ/).", 2),
    ("Grammar", "Quantifiers", "There isn't ___ milk in the fridge.",
     ["some", "any", "many"], 1, "Em frases negativas usa-se 'any'.", 2),
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
     ["am", "was", "were"], 2, "2nd conditional (hipotético): 'were' para todas as pessoas.", 3),
    ("Grammar", "Gerund/Infinitive", "I enjoy ___ to music.",
     ["listen", "to listen", "listening"], 2, "'enjoy' é seguido de gerúndio (-ing).", 2),
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


out = {"cards": cards}
path = os.path.join(os.path.dirname(__file__), "seed_cards.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

from collections import Counter
print(f"OK: {len(cards)} cards ->", path)
print("tipos:", dict(Counter(c["tipo"] for c in cards)))
print("topicos:", dict(Counter(c["topico"] for c in cards)))
