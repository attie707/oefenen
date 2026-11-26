"""Lessons: how Ukrainian works, for an English speaker. Explanations in English, examples in Ukrainian.

Roles (colours in the app):
  s = who            v = the verb          n = не / ні (not / no)
  q = question word  c = це / є            g = my (мій / моя / моє)
  t = place / time   r = the rest
Practice items: choice (q, options, answer, why, say?) or build (uk, en, alts).
"hide_tr": True hides the Latin letters (when they would give the answer away).
"""
import re

from . import content as C

LESSONS = [
    {
        "id": "u1", "title": "1. Reading Cyrillic", "short": "Friends, false friends and new letters", "practise": "a-read/alle",
        "cards": [
            {"title": "Easy: letters that work like ours",
             "text": "Some letters look and sound (almost) the same as in English: А (a), К (k), М (m), О (o), Т (t), "
                     "Е (e as in 'bed'). І is 'ee' as in 'see'. With only these you can already read your first words.",
             "examples": [([("мама", "r")], "mum"), ([("тато", "r")], "dad"), ([("кіт", "r")], "cat"), ([("так", "r")], "yes")],
             "tip": "Ukrainian is read the way it is written: every letter is pronounced, always the same way."},
            {"title": "Careful: false friends",
             "text": "These look English but are NOT: В = v · Н = n · Р = r (rolled) · С = s · У = oo · "
                     "Х = kh (like 'loch') · И = a short 'i' as in 'sit'.",
             "examples": [([("вона", "r")], "she (v-o-n-a)"), ([("ніс", "r")], "nose (n-ee-s)"),
                          ([("рука", "r")], "hand (r-oo-k-a)"), ([("син", "r")], "son (s-i-n)"), ([("хата", "r")], "house (kh-a-t-a)")],
             "tip": "Р is never 'p' and Н is never 'h'. Say РОТ (mouth) out loud: 'rot'."},
            {"title": "New shapes",
             "text": "Б b · Г h (soft, as in 'hello') · Ґ g · Д d · Ж zh (as in 'pleasure') · З z · Й y (as in 'boy') · Л l · "
                     "П p · Ф f · Ц ts · Ч ch · Ш sh · Щ shch · Ю yu · Я ya · Є ye · Ї yi. "
                     "Ь (soft sign) has no sound of its own: it makes the letter before it soft.",
             "examples": [([("привіт", "r")], "hi"), ([("дякую", "r")], "thank you"), ([("добре", "r")], "good / fine")],
             "tip": "Each word has one stressed syllable, but the spelling doesn't show which. Tap 🔊 and copy the sound. "
                    "The full alphabet is under 📜 on the home page."},
        ],
        "practice": [
            {"type": "choice", "q": "How do you read РОТ (mouth)?", "options": ["rot", "pot", "pom"], "answer": 0,
             "why": "Р = r, О = o, Т = t.", "say": "рот", "hide_tr": True},
            {"type": "choice", "q": "How do you read СИН (son)?", "options": ["syn", "cuh", "sun"], "answer": 0,
             "why": "С = s, И = short i, Н = n.", "say": "син", "hide_tr": True},
            {"type": "choice", "q": "How do you read ХАТА (house)?", "options": ["khata", "xata", "hata"], "answer": 0,
             "why": "Х = kh, like the end of 'loch'.", "say": "хата", "hide_tr": True},
            {"type": "choice", "q": "Which letter sounds like English 'v'?", "options": ["В", "Б", "Ф"], "answer": 0,
             "why": "В looks like a B, but it is a v. Б is the b.", "hide_tr": True},
            {"type": "choice", "q": "Which letter is the 'h' of 'hello'?", "options": ["Г", "Х", "Н"], "answer": 0,
             "why": "Г = h. Х is the harder 'kh', and Н is an n.", "hide_tr": True},
        ],
    },
    {
        "id": "u2", "title": "2. This is… · no 'am/is/are'", "short": "Це мама · Я студент", "practise": "p-build/family",
        "cards": [
            {"title": "No 'am', 'is' or 'are'",
             "text": "In the present tense Ukrainian simply leaves out 'to be'. You say 'I student', 'he doctor'. "
                     "And 'this is' is just one word: це.",
             "examples": [([("Це", "c"), ("мама.", "r")], "This is mum."),
                          ([("Я", "s"), ("студент.", "r")], "I am a student."),
                          ([("Він", "s"), ("лікар.", "r")], "He is a doctor.")],
             "tip": "A woman says студентка: Я студентка."},
            {"title": "No 'a' and no 'the'",
             "text": "Ukrainian has no articles. кіт means 'a cat' and 'the cat'. The situation tells you which one.",
             "examples": [([("Це", "c"), ("кіт.", "r")], "This is a cat. / This is the cat."),
                          ([("Це", "c"), ("мій", "g"), ("брат.", "r")], "This is my brother.")],
             "tip": "Що це? = What is this? Answer: Це … (This is …)."},
        ],
        "practice": [
            {"type": "choice", "q": "How do you say 'I am a teacher'?", "options": ["Я вчитель.", "Я є вчитель.", "Я а вчитель."],
             "answer": 0, "why": "No 'am' and no 'a': Я вчитель.", "say": "Я вчитель."},
            {"type": "choice", "q": "Це ___ means…", "options": ["this is", "there", "and"], "answer": 0,
             "why": "це = this is / that is.", "say": "це"},
            {"type": "build", "uk": "Це моя мама.", "en": "This is my mum.", "alts": []},
            {"type": "build", "uk": "Він лікар.", "en": "He is a doctor.", "alts": []},
        ],
    },
    {
        "id": "u3", "title": "3. I, you, he, she…", "short": "я · ти · ви · він · вона", "practise": "p-meaning/talk",
        "cards": [
            {"title": "The little words for people",
             "text": "я = I · ти = you · він = he · вона = she · воно = it · ми = we · ви = you (polite, or more people) · вони = they.",
             "examples": [([("Ти", "s"), ("мій друг.", "r")], "You are my friend."),
                          ([("Ми", "s"), ("вдома.", "t")], "We are at home."),
                          ([("Вони", "s"), ("в Україні.", "t")], "They are in Ukraine.")],
             "tip": "я is only written with a capital at the start of a sentence (unlike English 'I')."},
            {"title": "ти or ви?",
             "text": "ти is for one person you know well: family, friends, children. ви is for a stranger, an older person "
                     "or someone you show respect, and also for 'you all'.",
             "examples": [([("Як", "q"), ("ти?", "s")], "How are you? (to a friend)"),
                          ([("Ви", "s"), ("вчителька?", "r")], "Are you a teacher? (polite)")],
             "tip": "Not sure? Start with ви. People will tell you when you may say ти."},
        ],
        "practice": [
            {"type": "choice", "q": "'She' in Ukrainian is…", "options": ["він", "вона", "воно"], "answer": 1,
             "why": "він = he, вона = she, воно = it.", "say": "вона"},
            {"type": "choice", "q": "You talk to a shop assistant. Which 'you'?", "options": ["ти", "ви"], "answer": 1,
             "why": "A stranger gets the polite ви."},
            {"type": "choice", "q": "You talk to your daughter. Which 'you'?", "options": ["ти", "ви"], "answer": 0,
             "why": "Family and children get ти."},
            {"type": "build", "uk": "Ми вдома.", "en": "We are at home.", "alts": ["Вдома ми."]},
            {"type": "build", "uk": "Вони в Україні.", "en": "They are in Ukraine.", "alts": ["В Україні вони."]},
        ],
    },
    {
        "id": "u4", "title": "4. He, she or it: gender", "short": "мій брат · моя мама · моє вікно", "practise": "w-meaning/family",
        "cards": [
            {"title": "Every word is a 'he', a 'she' or an 'it'",
             "text": "You can usually see it at the end of the word. "
                     "Ends in a consonant → he (брат, кіт, стіл). "
                     "Ends in -а or -я → she (мама, кава, книга). "
                     "Ends in -о or -е → it (молоко, вікно, яблуко).",
             "examples": [([("Це", "c"), ("мій", "g"), ("брат.", "r")], "This is my brother."),
                          ([("Це", "c"), ("моя", "g"), ("мама.", "r")], "This is my mum."),
                          ([("Це", "c"), ("моє", "g"), ("вікно.", "r")], "This is my window.")],
             "tip": "'my' follows the word: мій for he-words, моя for she-words, моє for it-words."},
            {"title": "Things are 'he' or 'she' too",
             "text": "Because кава (coffee) is a she-word, you say вона (she) when you mean 'it'. "
                     "English says 'it', Ukrainian says 'she'.",
             "examples": [([("Де", "q"), ("кава?", "s")], "Where is the coffee?"),
                          ([("Вона", "s"), ("тут.", "t")], "It's here. (literally: she is here)")],
             "tip": "Same for 'your': твій (he) · твоя (she) · твоє (it)."},
        ],
        "practice": [
            {"type": "choice", "q": "молоко (milk) is…", "options": ["he (він)", "she (вона)", "it (воно)"], "answer": 2,
             "why": "It ends in -о, so it is an it-word.", "say": "молоко"},
            {"type": "choice", "q": "Це ___ книга.", "options": ["мій", "моя", "моє"], "answer": 1,
             "why": "книга ends in -а → she-word → моя.", "say": "Це моя книга."},
            {"type": "choice", "q": "Це ___ кіт.", "options": ["мій", "моя", "моє"], "answer": 0,
             "why": "кіт ends in a consonant → he-word → мій.", "say": "Це мій кіт."},
            {"type": "build", "uk": "Це моя донька.", "en": "This is my daughter.", "alts": []},
            {"type": "build", "uk": "Це мій син.", "en": "This is my son.", "alts": []},
        ],
    },
    {
        "id": "u5", "title": "5. Verbs: я знаю, ти знаєш", "short": "The ending shows who", "practise": "p-build/talk",
        "cards": [
            {"title": "The ending changes with the person",
             "text": "Many verbs end in -ати, like знати (to know) and читати (to read). Take off -ти and add: "
                     "я знаю · ти знаєш · він/вона знає · ми знаємо · ви знаєте · вони знають.",
             "examples": [([("Я", "s"), ("знаю.", "v")], "I know."),
                          ([("Ти", "s"), ("знаєш?", "v")], "Do you know?"),
                          ([("Вона", "s"), ("читає.", "v")], "She is reading. / She reads.")],
             "tip": "There's only one present tense: я читаю = I read and I am reading."},
            {"title": "The second group: -ити",
             "text": "Verbs like говорити (to speak) have slightly different endings: "
                     "я говорю · ти говориш · він говорить · ми говоримо · ви говорите · вони говорять.",
             "examples": [([("Ми", "s"), ("говоримо", "v"), ("українською.", "r")], "We speak Ukrainian."),
                          ([("Вони", "s"), ("говорять", "v"), ("англійською.", "r")], "They speak English.")],
             "tip": "Because the ending already shows who, you can often drop я/ти: Знаю! = I know!"},
        ],
        "practice": [
            {"type": "choice", "q": "Ти ___ українською?", "options": ["говорю", "говориш", "говорить"], "answer": 1,
             "why": "ти → -иш: ти говориш.", "say": "Ти говориш українською?"},
            {"type": "choice", "q": "Ми ___. (знати)", "options": ["знаю", "знаємо", "знають"], "answer": 1,
             "why": "ми → -ємо: ми знаємо.", "say": "Ми знаємо."},
            {"type": "choice", "q": "Вони ___. (читати)", "options": ["читає", "читаємо", "читають"], "answer": 2,
             "why": "вони → -ють: вони читають.", "say": "Вони читають."},
            {"type": "build", "uk": "Ми говоримо українською.", "en": "We speak Ukrainian.", "alts": ["Ми українською говоримо."]},
            {"type": "build", "uk": "Вона читає книгу.", "en": "She is reading a book.", "alts": ["Книгу читає вона.", "Вона книгу читає."]},
        ],
    },
    {
        "id": "u6", "title": "6. Asking questions", "short": "Де ти живеш?", "practise": "p-build/talk",
        "cards": [
            {"title": "Yes/no question: same words, voice goes up",
             "text": "You don't need 'do' or 'does'. Take a normal sentence and let your voice go up at the end. "
                     "You may put чи in front to make it extra clear.",
             "examples": [([("Ти", "s"), ("говориш", "v"), ("англійською?", "r")], "Do you speak English?"),
                          ([("Чи", "q"), ("ти", "s"), ("говориш", "v"), ("англійською?", "r")], "Do you speak English?")]},
            {"title": "Question words go first",
             "text": "хто = who · що = what · де = where · звідки = where from · коли = when · як = how · "
                     "чому = why · скільки = how much / how many.",
             "examples": [([("Де", "q"), ("ти", "s"), ("живеш?", "v")], "Where do you live?"),
                          ([("Що", "q"), ("це?", "c")], "What is this?"),
                          ([("Звідки", "q"), ("ви?", "s")], "Where are you from?"),
                          ([("Скільки", "q"), ("це коштує?", "r")], "How much does it cost?")],
             "tip": "що is pronounced 'shcho': Щ is one letter."},
        ],
        "practice": [
            {"type": "choice", "q": "'Where' is…", "options": ["де", "коли", "хто"], "answer": 0,
             "why": "де = where, коли = when, хто = who.", "say": "де"},
            {"type": "choice", "q": "How do you ask 'Do you live here?'", "options": ["Ти живеш тут?", "Чи ти живеш тут?", "Both are fine"],
             "answer": 2, "why": "Same words with a rising voice. чи in front is optional."},
            {"type": "build", "uk": "Де ти живеш?", "en": "Where do you live?", "alts": ["Де живеш ти?"]},
            {"type": "build", "uk": "Як тебе звати?", "en": "What is your name?", "alts": []},
        ],
    },
    {
        "id": "u7", "title": "7. No and not: не, ні", "short": "Я не знаю", "practise": "p-meaning/talk",
        "cards": [
            {"title": "не goes right before the verb",
             "text": "Put не (not) in front of the word you want to deny, usually the verb. "
                     "There's no 'don't' or 'doesn't': 'I not know'.",
             "examples": [([("Я", "s"), ("не", "n"), ("знаю.", "v")], "I don't know."),
                          ([("Я", "s"), ("не", "n"), ("розумію.", "v")], "I don't understand."),
                          ([("Це", "c"), ("не", "n"), ("мій", "g"), ("кіт.", "r")], "This isn't my cat.")]},
            {"title": "Yes and no",
             "text": "так = yes · ні = no. ні is the answer, не is 'not' inside a sentence.",
             "examples": [([("Ні,", "n"), ("дякую.", "r")], "No, thank you."),
                          ([("Так,", "r"), ("я", "s"), ("знаю.", "v")], "Yes, I know.")],
             "tip": "Тут немає кави = There's no coffee here. немає = 'there is no'. The word after it changes a little (кава → кави)."},
        ],
        "practice": [
            {"type": "choice", "q": "'I don't understand.'", "options": ["Я не розумію.", "Я розумію не.", "Не я розумію."], "answer": 0,
             "why": "не goes right before the verb.", "say": "Я не розумію."},
            {"type": "choice", "q": "'Yes' is…", "options": ["так", "ні", "не"], "answer": 0, "why": "так = yes, ні = no.", "say": "так"},
            {"type": "build", "uk": "Я не говорю українською.", "en": "I don't speak Ukrainian.", "alts": []},
            {"type": "build", "uk": "Це не моя кава.", "en": "This isn't my coffee.", "alts": []},
        ],
    },
    {
        "id": "u8", "title": "8. I have… · my name is…", "short": "У мене є · Мене звати", "practise": "p-build/family",
        "cards": [
            {"title": "'I have' = 'at me there is'",
             "text": "To say what you have, Ukrainian usually says у мене є (literally: at me there is). "
                     "у тебе є = you have · у нас є = we have.",
             "examples": [([("У мене", "s"), ("є", "c"), ("брат.", "r")], "I have a brother."),
                          ([("У тебе", "s"), ("є", "c"), ("кіт?", "r")], "Do you have a cat?"),
                          ([("У нас", "s"), ("є", "c"), ("машина.", "r")], "We have a car.")],
             "tip": "Don't have: У мене немає часу = I don't have time. Here too the word after немає changes (час → часу)."},
            {"title": "'My name is' = 'me they call'",
             "text": "Мене звати … literally means 'me (they) call …'. To ask: Як тебе звати? (friend) or Як вас звати? (polite).",
             "examples": [([("Мене звати", "r"), ("Анна.", "r")], "My name is Anna."),
                          ([("Як", "q"), ("тебе звати?", "r")], "What's your name? (friend)"),
                          ([("Як", "q"), ("вас звати?", "r")], "What's your name? (polite)")]},
        ],
        "practice": [
            {"type": "choice", "q": "'I have a sister.'", "options": ["У мене є сестра.", "Мене є сестра.", "Я є сестра."], "answer": 0,
             "why": "у мене є = I have.", "say": "У мене є сестра."},
            {"type": "choice", "q": "How do you ask a stranger their name?", "options": ["Як вас звати?", "Як тебе звати?"], "answer": 0,
             "why": "A stranger gets the polite вас.", "say": "Як вас звати?"},
            {"type": "build", "uk": "У мене є брат.", "en": "I have a brother.", "alts": []},
            {"type": "build", "uk": "Мене звати Анна.", "en": "My name is Anna.", "alts": []},
        ],
    },
]
LESSON_BY_ID = {l["id"]: l for l in LESSONS}
PROPER = C.PROPER | {"Україні", "Анна"}
CYR = re.compile(r"[а-яіїєґА-ЯІЇЄҐ]")


def sentence(parts):
    return " ".join(p for p, _ in parts)


def tr(s):
    return C.translit(s) if s and CYR.search(s) else None


def tiles(s):
    return [w if w in PROPER else w.lower() for w in re.sub(r"[.,!?]", "", s).split()]


def phrases():
    out = set()
    for l in LESSONS:
        for c in l["cards"]:
            for parts, _ in c["examples"]:
                out.add(sentence(parts))
        for p in l["practice"]:
            if p["type"] == "build":
                out.add(p["uk"])
            elif p.get("say"):
                out.add(p["say"])
    return out


def public(lesson):
    """Lesson as sent to the app, with Latin letters added."""
    practice = []
    for p in lesson["practice"]:
        p = dict(p)
        if p["type"] == "build":
            words = tiles(p["uk"])
            p.update(tiles=words, tiles_tr=[C.translit(w) for w in words], tr=C.translit(p["uk"]))
        elif not p.get("hide_tr"):
            p.update(q_tr=tr(p["q"]), opt_tr=[tr(o) for o in p["options"]])
        practice.append(p)
    return {"id": lesson["id"], "title": lesson["title"], "short": lesson["short"], "practise": lesson["practise"],
            "cards": [{"title": c["title"], "text": c["text"], "tip": c.get("tip"),
                       "examples": [{"parts": [list(x) for x in parts], "say": sentence(parts), "tr": C.translit(sentence(parts)),
                                     "en": en} for parts, en in c["examples"]]} for c in lesson["cards"]],
            "practice": practice}
