"""Lessons: how to build a Dutch sentence (A1-A2). Explanations in English, examples in Dutch.

Roles (colours in the app):
  s = who (subject)        v = the verb (always place 2 in a normal sentence)
  v2 = second verb / end   t = time or place      n = niet / geen
  q = question word        c = omdat, dat, als…   r = the rest
"""

LESSONS = [
    {
        "id": "l1", "title": "1. The basic sentence", "short": "Who → verb → rest", "practise": "gewoon",
        "cards": [
            {"title": "The verb is always in place 2",
             "text": "A normal Dutch sentence starts with WHO does something. Then comes the VERB. Then the rest. "
                     "Think of a train: the red verb is always the second wagon.",
             "examples": [
                 ([("Ik", "s"), ("woon", "v"), ("in Utrecht.", "r")], "I live in Utrecht."),
                 ([("Wij", "s"), ("eten", "v"), ("om zes uur.", "t")], "We eat at six o'clock."),
                 ([("Mijn naam", "s"), ("is", "v"), ("Anna.", "r")], "My name is Anna."),
             ],
             "tip": "Count blocks, not words: 'Mijn naam' is one block, so 'is' is still in place 2."},
            {"title": "The verb changes with the person",
             "text": "ik → just the stem (werk). jij / u / hij / zij → stem + t (werkt). wij / jullie / zij → the whole verb (werken).",
             "examples": [
                 ([("Ik", "s"), ("werk", "v"), ("in een winkel.", "r")], "I work in a shop."),
                 ([("Hij", "s"), ("werkt", "v"), ("in een winkel.", "r")], "He works in a shop."),
                 ([("Wij", "s"), ("werken", "v"), ("in een winkel.", "r")], "We work in a shop."),
             ],
             "tip": "Practise the forms in Werkwoorden → level 2."},
        ],
        "practice": [
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["Ik woon in Utrecht.", "Ik in Utrecht woon.", "Woon in Utrecht ik."],
             "answer": 0, "why": "Who (Ik) → verb (woon) → rest (in Utrecht)."},
            {"type": "choice", "q": "Hij ___ in Amsterdam.", "options": ["woon", "woont", "wonen"],
             "answer": 1, "why": "hij → stem + t: hij woont."},
            {"type": "build", "nl": "Ik drink elke ochtend koffie.", "en": "I drink coffee every morning.",
             "alts": ["Elke ochtend drink ik koffie."]},
            {"type": "build", "nl": "De kinderen spelen in de tuin.", "en": "The children play in the garden.",
             "alts": ["In de tuin spelen de kinderen."]},
        ],
    },
    {
        "id": "l2", "title": "2. Asking questions", "short": "Verb first · werk jij?", "practise": "vragen",
        "cards": [
            {"title": "Yes/no question: put the verb first",
             "text": "Turn a sentence into a question by putting the VERB at the start. Then who, then the rest.",
             "examples": [
                 ([("Spreek", "v"), ("jij", "s"), ("Nederlands?", "r")], "Do you speak Dutch?"),
                 ([("Woont", "v"), ("hij", "s"), ("hier?", "t")], "Does he live here?"),
                 ([("Heb", "v"), ("jij", "s"), ("een broer?", "r")], "Do you have a brother?"),
             ],
             "tip": "Important: when jij/je comes AFTER the verb, the -t disappears: jij werkt → werk jij? "
                    "This is only for jij/je, not for hij: woont hij?"},
            {"title": "Question word first, then the verb",
             "text": "With a question word the order is: question word → verb → who → rest. "
                     "wie = who · wat = what · waar = where · wanneer = when · hoe = how · waarom = why · hoeveel = how much.",
             "examples": [
                 ([("Waar", "q"), ("woon", "v"), ("jij?", "s")], "Where do you live?"),
                 ([("Hoe", "q"), ("heet", "v"), ("jij?", "s")], "What is your name?"),
                 ([("Wat", "q"), ("drink", "v"), ("jij?", "s")], "What are you drinking?"),
                 ([("Hoe laat", "q"), ("is", "v"), ("het?", "s")], "What time is it?"),
             ],
             "tip": "The verb is still in place 2: the question word takes place 1."},
        ],
        "practice": [
            {"type": "choice", "q": "Which question is correct?",
             "options": ["Werk jij morgen?", "Werkt jij morgen?", "Jij werk morgen?"],
             "answer": 0, "why": "jij comes after the verb, so no -t: werk jij?"},
            {"type": "choice", "q": "Which question is correct?",
             "options": ["Waar woont hij?", "Waar hij woont?", "Waar woon hij?"],
             "answer": 0, "why": "Question word → verb → who. hij keeps the -t: woont hij."},
            {"type": "build", "nl": "Spreek jij Nederlands?", "en": "Do you speak Dutch?", "alts": []},
            {"type": "build", "nl": "Waar is het station?", "en": "Where is the station?", "alts": []},
        ],
    },
    {
        "id": "l3", "title": "3. Time or place first", "short": "Morgen ga ik…", "practise": "inversie",
        "cards": [
            {"title": "Start with time or place? Then who and verb swap",
             "text": "You may start a sentence with WHEN or WHERE. The verb wants to stay in place 2, "
                     "so 'who' moves behind the verb.",
             "examples": [
                 ([("Ik", "s"), ("ga", "v"), ("morgen", "t"), ("naar de markt.", "r")], "I'm going to the market tomorrow."),
                 ([("Morgen", "t"), ("ga", "v"), ("ik", "s"), ("naar de markt.", "r")], "Tomorrow I'm going to the market."),
                 ([("Vandaag", "t"), ("werk", "v"), ("ik", "s"), ("thuis.", "t")], "Today I work at home."),
             ]},
            {"title": "Long time words count as one block",
             "text": "'In de zomer', 'Op zaterdag' and 'Om acht uur' are one block each. The verb comes right after the block.",
             "examples": [
                 ([("In de zomer", "t"), ("fietsen", "v"), ("wij", "s"), ("veel.", "r")], "In summer we cycle a lot."),
                 ([("Gisteren", "t"), ("was", "v"), ("het", "s"), ("koud.", "r")], "Yesterday it was cold."),
             ],
             "tip": "Never two blocks before the verb: 'Vandaag ik werk' is wrong."},
        ],
        "practice": [
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["Vandaag werk ik thuis.", "Vandaag ik werk thuis.", "Vandaag ik thuis werk."],
             "answer": 0, "why": "After 'Vandaag' comes the verb (werk), then who (ik)."},
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["Op zaterdag doe ik boodschappen.", "Op zaterdag ik doe boodschappen.", "Op zaterdag doe boodschappen ik."],
             "answer": 0, "why": "'Op zaterdag' is one block, then the verb (doe), then who (ik)."},
            {"type": "build", "nl": "Om acht uur kijk ik televisie.", "en": "At eight o'clock I watch TV.",
             "alts": ["Ik kijk om acht uur televisie."]},
            {"type": "build", "nl": "Morgen ga ik naar de markt.", "en": "Tomorrow I'm going to the market.",
             "alts": ["Ik ga morgen naar de markt."]},
        ],
    },
    {
        "id": "l4", "title": "4. niet or geen?", "short": "Saying 'no' and 'not'", "practise": "ontkenning",
        "cards": [
            {"title": "geen = 'no' / 'not a' before a thing",
             "text": "Use geen before a noun that has 'een' or no article at all. 'een' becomes 'geen'.",
             "examples": [
                 ([("Ik", "s"), ("heb", "v"), ("geen", "n"), ("auto.", "r")], "I don't have a car. (Ik heb een auto.)"),
                 ([("Ik", "s"), ("drink", "v"), ("geen", "n"), ("koffie.", "r")], "I don't drink coffee. (Ik drink koffie.)"),
                 ([("Wij", "s"), ("hebben", "v"), ("geen", "n"), ("tijd.", "r")], "We have no time."),
             ]},
            {"title": "niet = all other cases",
             "text": "Use niet for verbs, adjectives, places and 'het/de' words. Usually niet goes to the END. "
                     "But niet comes BEFORE an adjective or a place.",
             "examples": [
                 ([("Ik", "s"), ("begrijp", "v"), ("het", "r"), ("niet.", "n")], "I don't understand it."),
                 ([("Zij", "s"), ("komt", "v"), ("vandaag", "t"), ("niet.", "n")], "She's not coming today."),
                 ([("Het", "s"), ("is", "v"), ("niet", "n"), ("ver.", "r")], "It's not far."),
             ],
             "tip": "Quick test: could you say 'een' or nothing before the word? → geen. Otherwise → niet."},
        ],
        "practice": [
            {"type": "choice", "q": "Ik heb ___ tijd.", "options": ["geen", "niet"], "answer": 0,
             "why": "tijd is a thing without 'een' or 'de' → geen."},
            {"type": "choice", "q": "Ik begrijp het ___.", "options": ["niet", "geen"], "answer": 0,
             "why": "It's not about a thing with 'een' → niet, at the end."},
            {"type": "choice", "q": "Het is ___ ver.", "options": ["niet", "geen"], "answer": 0,
             "why": "ver is an adjective → niet, before it."},
            {"type": "build", "nl": "Hij heeft geen auto.", "en": "He doesn't have a car.", "alts": []},
            {"type": "build", "nl": "Zij komt vandaag niet.", "en": "She's not coming today.", "alts": ["Vandaag komt zij niet."]},
        ],
    },
    {
        "id": "l5", "title": "5. Two verbs", "short": "Ik wil … leren", "practise": "modaal",
        "cards": [
            {"title": "The second verb goes to the end",
             "text": "With willen, kunnen, moeten, mogen and gaan you use two verbs. The first one is in place 2 "
                     "and changes with the person. The second one stays whole and goes to the very END.",
             "examples": [
                 ([("Ik", "s"), ("wil", "v"), ("Nederlands", "r"), ("leren.", "v2")], "I want to learn Dutch."),
                 ([("Zij", "s"), ("kan", "v"), ("goed", "r"), ("koken.", "v2")], "She can cook well."),
                 ([("Wij", "s"), ("moeten", "v"), ("morgen", "t"), ("werken.", "v2")], "We have to work tomorrow."),
             ]},
            {"title": "gaan + verb = the future",
             "text": "'Ik ga …' + a whole verb at the end is the easy way to talk about the future.",
             "examples": [
                 ([("Ik", "s"), ("ga", "v"), ("morgen", "t"), ("fietsen.", "v2")], "I'm going to cycle tomorrow."),
                 ([("Kun", "v"), ("jij", "s"), ("mij", "r"), ("helpen?", "v2")], "Can you help me?"),
             ],
             "tip": "In questions too, the second verb stays at the end."},
        ],
        "practice": [
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["Wij moeten morgen werken.", "Wij moeten werken morgen.", "Wij werken moeten morgen."],
             "answer": 0, "why": "First verb in place 2 (moeten), second verb at the end (werken)."},
            {"type": "build", "nl": "Ik wil Nederlands leren.", "en": "I want to learn Dutch.", "alts": []},
            {"type": "build", "nl": "Zij kan goed koken.", "en": "She can cook well.", "alts": []},
            {"type": "build", "nl": "Kun jij mij helpen?", "en": "Can you help me?", "alts": []},
        ],
    },
    {
        "id": "l6", "title": "6. Talking about the past", "short": "heb … gewerkt", "practise": "voltooid",
        "cards": [
            {"title": "hebben / zijn + ge-word at the end",
             "text": "Dutch people mostly talk about the past with hebben or zijn in place 2, "
                     "and a 'ge-word' (past participle) at the END.",
             "examples": [
                 ([("Ik", "s"), ("heb", "v"), ("gisteren", "t"), ("gewerkt.", "v2")], "I worked yesterday."),
                 ([("Hij", "s"), ("heeft", "v"), ("een fiets", "r"), ("gekocht.", "v2")], "He bought a bike."),
                 ([("Wij", "s"), ("zijn", "v"), ("naar Amsterdam", "t"), ("gegaan.", "v2")], "We went to Amsterdam."),
             ]},
            {"title": "Making the ge-word",
             "text": "Regular verbs: ge + stem + t or d. Use t when the stem ends in t, k, f, s, ch or p "
                     "(remember: 't kofschip). Otherwise d: werken → gewerkt, wonen → gewoond, spelen → gespeeld. "
                     "Irregular ones you just learn: gelezen, gekocht, gegaan, gebleven, gegeten.",
             "examples": [
                 ([("Ik", "s"), ("heb", "v"), ("in Utrecht", "t"), ("gewoond.", "v2")], "I lived in Utrecht."),
                 ([("Heb", "v"), ("jij", "s"), ("het boek", "r"), ("gelezen?", "v2")], "Have you read the book?"),
             ]},
            {"title": "hebben or zijn?",
             "text": "Most verbs use hebben. Use zijn for going somewhere or a change: gaan, komen, blijven, worden.",
             "examples": [
                 ([("Zij", "s"), ("is", "v"), ("thuis", "t"), ("gebleven.", "v2")], "She stayed at home."),
                 ([("Ik", "s"), ("heb", "v"), ("mijn sleutel", "r"), ("verloren.", "v2")], "I lost my key."),
             ]},
        ],
        "practice": [
            {"type": "choice", "q": "Wij ___ naar Amsterdam gegaan.", "options": ["zijn", "hebben"], "answer": 0,
             "why": "gaan = going somewhere → zijn."},
            {"type": "choice", "q": "Ik heb gisteren ___.", "options": ["gewerkt", "gewerkd", "werkte"], "answer": 0,
             "why": "werk ends in k ('t kofschip) → gewerkt."},
            {"type": "build", "nl": "Ik heb gisteren gewerkt.", "en": "I worked yesterday.", "alts": ["Gisteren heb ik gewerkt."]},
            {"type": "build", "nl": "Hij heeft een fiets gekocht.", "en": "He bought a bike.", "alts": []},
        ],
    },
    {
        "id": "l7", "title": "7. Separable verbs", "short": "Ik bel je op", "practise": None,
        "cards": [
            {"title": "The little front word goes to the end",
             "text": "Some verbs start with a small word: opbellen (to call), opruimen (to tidy up), meenemen (to take along), "
                     "aankomen (to arrive). In a normal sentence that small word breaks off and goes to the END.",
             "examples": [
                 ([("Ik", "s"), ("bel", "v"), ("je", "r"), ("morgen", "t"), ("op.", "v2")], "I'll call you tomorrow. (opbellen)"),
                 ([("Ik", "s"), ("ruim", "v"), ("mijn kamer", "r"), ("op.", "v2")], "I'm tidying my room. (opruimen)"),
                 ([("De trein", "s"), ("komt", "v"), ("om acht uur", "t"), ("aan.", "v2")], "The train arrives at eight. (aankomen)"),
             ]},
            {"title": "With two verbs they stay together",
             "text": "If the verb is the second verb at the end, it stays in one piece. In the past, 'ge' goes in the middle: opgeruimd.",
             "examples": [
                 ([("Ik", "s"), ("wil", "v"), ("je", "r"), ("morgen", "t"), ("opbellen.", "v2")], "I want to call you tomorrow."),
                 ([("Ik", "s"), ("heb", "v"), ("mijn kamer", "r"), ("opgeruimd.", "v2")], "I have tidied my room."),
             ]},
        ],
        "practice": [
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["De trein komt om acht uur aan.", "De trein aankomt om acht uur."], "answer": 0,
             "why": "aankomen splits: komt … aan."},
            {"type": "build", "nl": "Ik bel je morgen op.", "en": "I'll call you tomorrow.", "alts": ["Morgen bel ik je op."]},
            {"type": "build", "nl": "Ik ruim mijn kamer op.", "en": "I'm tidying my room.", "alts": []},
            {"type": "build", "nl": "Ik wil je morgen opbellen.", "en": "I want to call you tomorrow.", "alts": ["Morgen wil ik je opbellen."]},
        ],
    },
    {
        "id": "l8", "title": "8. omdat, dat, als", "short": "The verb goes to the end", "practise": "bijzin",
        "cards": [
            {"title": "After omdat, dat, als: verb at the end",
             "text": "After omdat (because), dat (that), als (if/when), of (whether) and question words in the middle "
                     "of a sentence, the verb goes to the END of that part.",
             "examples": [
                 ([("Ik", "s"), ("blijf", "v"), ("thuis,", "t"), ("omdat", "c"), ("ik", "s"), ("ziek", "r"), ("ben.", "v2")], "I'm staying home because I'm ill."),
                 ([("Ik", "s"), ("denk", "v"), ("dat", "c"), ("het", "s"), ("gaat regenen.", "v2")], "I think it's going to rain."),
                 ([("Ik", "s"), ("weet", "v"), ("niet", "n"), ("waar", "c"), ("hij", "s"), ("woont.", "v2")], "I don't know where he lives."),
             ]},
            {"title": "want, maar, en: normal order",
             "text": "want (because), maar (but) and en (and) do NOT change anything: after them the order is normal.",
             "examples": [
                 ([("Ik", "s"), ("blijf", "v"), ("thuis,", "t"), ("want", "c"), ("ik", "s"), ("ben", "v"), ("ziek.", "r")], "I'm staying home, because I'm ill."),
             ],
             "tip": "omdat and want both mean 'because', but: omdat → verb at the end, want → normal order."},
            {"title": "Starting with the omdat/als part",
             "text": "If the sentence starts with the als/omdat part, that whole part is place 1. "
                     "So the next word is the verb: verb, comma, verb.",
             "examples": [
                 ([("Als het mooi weer is,", "c"), ("gaan", "v"), ("wij", "s"), ("naar het strand.", "t")], "If the weather is nice, we go to the beach."),
             ]},
        ],
        "practice": [
            {"type": "choice", "q": "Ik blijf thuis, ___ ik ben ziek.", "options": ["want", "omdat"], "answer": 0,
             "why": "'ik ben ziek' has normal order → want. With omdat it would be: omdat ik ziek ben."},
            {"type": "choice", "q": "Which sentence is correct?",
             "options": ["Ik weet niet waar hij woont.", "Ik weet niet waar woont hij."], "answer": 0,
             "why": "waar in the middle of the sentence → verb (woont) at the end."},
            {"type": "build", "nl": "Ik blijf thuis, omdat ik ziek ben.", "en": "I'm staying home because I'm ill.",
             "alts": ["Omdat ik ziek ben, blijf ik thuis."]},
            {"type": "build", "nl": "Als het mooi weer is, gaan wij naar het strand.", "en": "If the weather is nice, we go to the beach.",
             "alts": ["Wij gaan naar het strand als het mooi weer is."]},
        ],
    },
]
LESSON_BY_ID = {l["id"]: l for l in LESSONS}
LESSON_FOR_CAT = {l["practise"]: l["id"] for l in LESSONS if l["practise"]}


def sentence(parts):
    return " ".join(p for p, _ in parts)


def phrases():
    out = set()
    for l in LESSONS:
        for c in l["cards"]:
            for parts, _ in c["examples"]:
                out.add(sentence(parts))
        for p in l["practice"]:
            if p["type"] == "build":
                out.add(p["nl"])
            elif len(p["options"][p["answer"]]) > 12:      # a full correct sentence
                out.add(p["options"][p["answer"]])
    return out


def public(lesson):
    """Lesson as sent to the app."""
    return {"id": lesson["id"], "title": lesson["title"], "short": lesson["short"], "practise": lesson["practise"],
            "cards": [{"title": c["title"], "text": c["text"], "tip": c.get("tip"),
                       "examples": [{"parts": [list(p) for p in parts], "say": sentence(parts), "en": en}
                                    for parts, en in c["examples"]]} for c in lesson["cards"]],
            "practice": lesson["practice"]}
