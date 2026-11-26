"""Ukrainian for beginners: the Cyrillic alphabet, everyday words and family phrases.
Translations in English (en) and Dutch (nl).

Add words in WORDS:   ("українське слово", "emoji", "english", "nederlands")
Add phrases in PHRASES: ("Фраза.", "english", "nederlands")
"""
import random
import re

# ---------------------------------------------------------------- transliteration (learner friendly)
TR = {"а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d", "е": "e", "є": "ye", "ж": "zh", "з": "z",
      "и": "y", "і": "i", "ї": "yi", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
      "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh",
      "щ": "shch", "ь": "'", "ю": "yu", "я": "ya", "'": "", "ʼ": "", "’": ""}


def translit(text):
    out = []
    for ch in text:
        low = ch.lower()
        if low in TR:
            t = TR[low]
            out.append(t[:1].upper() + t[1:] if ch != low and t else t)
        else:
            out.append(ch)
    return "".join(out)


# ---------------------------------------------------------------- alphabet
# letter, letter name (spoken), example word, emoji, example meaning en, nl, sound hint en, nl
ALPHABET = [
    ("А", "а", "ананас", "🍍", "pineapple", "ananas", "a as in 'father'", "a als in 'bal'"),
    ("Б", "бе", "банан", "🍌", "banana", "banaan", "b", "b"),
    ("В", "ве", "вода", "💧", "water", "water", "v (looks like B!)", "v of w (lijkt op een B!)"),
    ("Г", "ге", "гора", "⛰️", "mountain", "berg", "a soft h, as in 'ahead'", "zachte g/h, zoals in 'goed'"),
    ("Ґ", "ґе", "ґудзик", "🔘", "button", "knoop", "g as in 'go'", "g als in het Engelse 'go'"),
    ("Д", "де", "дім", "🏠", "house", "huis", "d", "d"),
    ("Е", "е", "мед", "🍯", "honey", "honing", "e as in 'bed'", "e als in 'bed'"),
    ("Є", "є", "єнот", "🦝", "raccoon", "wasbeer", "ye as in 'yes'", "je als in 'jet'"),
    ("Ж", "же", "жаба", "🐸", "frog", "kikker", "s as in 'pleasure'", "g als in 'garage'"),
    ("З", "зе", "зебра", "🦓", "zebra", "zebra", "z as in 'zoo'", "z als in 'zoo'"),
    ("И", "и", "кит", "🐋", "whale", "walvis", "i as in 'sit'", "i als in 'pit'"),
    ("І", "і", "індик", "🦃", "turkey", "kalkoen", "ee as in 'see'", "ie als in 'zien'"),
    ("Ї", "ї", "їжак", "🦔", "hedgehog", "egel", "yee as in 'yeast'", "jie"),
    ("Й", "йот", "йогурт", "🥣", "yoghurt", "yoghurt", "y as in 'boy'", "j als in 'ja'"),
    ("К", "ка", "кіт", "🐈", "cat", "kat", "k", "k"),
    ("Л", "ел", "лев", "🦁", "lion", "leeuw", "l", "l"),
    ("М", "ем", "мама", "👩", "mum", "mama", "m", "m"),
    ("Н", "ен", "ніс", "👃", "nose", "neus", "n (looks like H!)", "n (lijkt op een H!)"),
    ("О", "о", "око", "👁️", "eye", "oog", "o as in 'more'", "o als in 'pot'"),
    ("П", "пе", "птах", "🐦", "bird", "vogel", "p", "p"),
    ("Р", "ер", "риба", "🐟", "fish", "vis", "a rolled r (looks like P!)", "gerolde r (lijkt op een P!)"),
    ("С", "ес", "сонце", "☀️", "sun", "zon", "s (looks like C!)", "s (lijkt op een C!)"),
    ("Т", "те", "тато", "👨", "dad", "papa", "t", "t"),
    ("У", "у", "Україна", "🇺🇦", "Ukraine", "Oekraïne", "oo as in 'moon' (looks like y!)", "oe als in 'boek' (lijkt op een y!)"),
    ("Ф", "еф", "футбол", "⚽", "football", "voetbal", "f", "f"),
    ("Х", "ха", "хліб", "🍞", "bread", "brood", "ch as in Scottish 'loch' (looks like X!)", "ch als in 'lachen' (lijkt op een X!)"),
    ("Ц", "це", "цибуля", "🧅", "onion", "ui", "ts as in 'cats'", "ts als in 'iets'"),
    ("Ч", "че", "чай", "🍵", "tea", "thee", "ch as in 'chair'", "tsj als in 'Tsjechië'"),
    ("Ш", "ша", "шапка", "🧢", "hat", "muts", "sh as in 'shop'", "sj als in 'sjaal'"),
    ("Щ", "ща", "борщ", "🍲", "borscht", "borsjtsj", "shch: 'fresh cheese' said fast", "sjtsj"),
    ("Ь", "м'який знак", "кінь", "🐎", "horse", "paard", "soft sign: makes the letter before it soft, no sound of its own",
     "zacht teken: maakt de letter ervoor zacht, geen eigen klank"),
    ("Ю", "ю", "салют", "🎆", "fireworks", "vuurwerk", "you", "joe"),
    ("Я", "я", "яблуко", "🍎", "apple", "appel", "ya as in 'yard'", "ja"),
]
LETTERS = {a[0]: {"up": a[0], "low": a[0].lower(), "name": a[1], "word": a[2], "emoji": a[3], "en": a[4], "nl": a[5],
                  "hint_en": a[6], "hint_nl": a[7], "sound": TR[a[0].lower()] or "'"} for a in ALPHABET}
LETTERS["Ь"]["sound"] = "'"
LETTER_GROUPS = {
    "g1": ({"en": "1. Same as in English", "nl": "1. Hetzelfde als bij ons"}, list("АЕІКМОТ")),
    "g2": ({"en": "2. Look-alikes, other sound", "nl": "2. Lijken bekend, andere klank"}, list("ВНРСУХИ")),
    "g3": ({"en": "3. New letters", "nl": "3. Nieuwe letters"}, list("БГҐДЄЖЗЇЙЛПФЦЧШЩЬЮЯ")),
}
GROUP_OF = {l: g for g, (_, ls) in LETTER_GROUPS.items() for l in ls}
# how a Dutch or English reader would wrongly read a Cyrillic letter
LOOKALIKE = {"В": "b", "Н": "h", "Р": "p", "С": "c", "У": "y", "Х": "x", "И": "n", "Е": "ye", "І": "y", "Г": "r"}

# ---------------------------------------------------------------- words
THEMES = {
    "family": ({"en": "Family", "nl": "Familie"}, [
        ("мама", "👩", "mum", "mama"), ("тато", "👨", "dad", "papa"), ("бабуся", "👵", "grandma", "oma"),
        ("дідусь", "👴", "grandpa", "opa"), ("син", "👦", "son", "zoon"), ("донька", "👧", "daughter", "dochter"),
        ("брат", "🧑", "brother", "broer"), ("сестра", "👱‍♀️", "sister", "zus"), ("дитина", "👶", "child", "kind"),
        ("сім'я", "👨‍👩‍👧", "family", "gezin"), ("чоловік", "🤵", "husband", "echtgenoot"),
        ("дружина", "👰", "wife", "echtgenote"), ("друг", "🤝", "friend", "vriend"),
    ]),
    "food": ({"en": "Food and drinks", "nl": "Eten en drinken"}, [
        ("хліб", "🍞", "bread", "brood"), ("вода", "💧", "water", "water"), ("молоко", "🥛", "milk", "melk"),
        ("чай", "🍵", "tea", "thee"), ("кава", "☕", "coffee", "koffie"), ("яблуко", "🍎", "apple", "appel"),
        ("банан", "🍌", "banana", "banaan"), ("сир", "🧀", "cheese", "kaas"), ("яйце", "🥚", "egg", "ei"),
        ("м'ясо", "🥩", "meat", "vlees"), ("риба", "🐟", "fish", "vis"), ("борщ", "🍲", "borscht", "borsjtsj"),
        ("картопля", "🥔", "potatoes", "aardappels"), ("помідор", "🍅", "tomato", "tomaat"),
        ("морква", "🥕", "carrot", "wortel"), ("вареники", "🥟", "dumplings (varenyky)", "deegkussentjes (varenyky)"),
        ("торт", "🎂", "cake", "taart"), ("сіль", "🧂", "salt", "zout"), ("цибуля", "🧅", "onion", "ui"),
        ("масло", "🧈", "butter", "boter"),
    ]),
    "animals": ({"en": "Animals", "nl": "Dieren"}, [
        ("кіт", "🐈", "cat", "kat"), ("собака", "🐕", "dog", "hond"), ("кінь", "🐎", "horse", "paard"),
        ("корова", "🐄", "cow", "koe"), ("свиня", "🐖", "pig", "varken"), ("курка", "🐔", "chicken", "kip"),
        ("птах", "🐦", "bird", "vogel"), ("миша", "🐭", "mouse", "muis"), ("ведмідь", "🐻", "bear", "beer"),
        ("лев", "🦁", "lion", "leeuw"), ("заєць", "🐇", "hare", "haas"), ("качка", "🦆", "duck", "eend"),
        ("жаба", "🐸", "frog", "kikker"), ("їжак", "🦔", "hedgehog", "egel"), ("вовк", "🐺", "wolf", "wolf"),
        ("лисиця", "🦊", "fox", "vos"),
    ]),
    "home": ({"en": "At home", "nl": "In huis"}, [
        ("дім", "🏠", "house", "huis"), ("двері", "🚪", "door", "deur"), ("вікно", "🪟", "window", "raam"),
        ("стілець", "🪑", "chair", "stoel"), ("ліжко", "🛏️", "bed", "bed"), ("книга", "📖", "book", "boek"),
        ("телефон", "📱", "phone", "telefoon"), ("ключ", "🔑", "key", "sleutel"), ("лампа", "💡", "lamp", "lamp"),
        ("годинник", "🕰️", "clock", "klok"), ("машина", "🚗", "car", "auto"),
    ]),
    "body": ({"en": "The body", "nl": "Het lichaam"}, [
        ("голова", "🧑", "head", "hoofd"), ("око", "👁️", "eye", "oog"), ("вухо", "👂", "ear", "oor"),
        ("ніс", "👃", "nose", "neus"), ("рот", "👄", "mouth", "mond"), ("рука", "✋", "hand / arm", "hand / arm"),
        ("нога", "🦵", "leg / foot", "been / voet"), ("зуб", "🦷", "tooth", "tand"), ("серце", "❤️", "heart", "hart"),
        ("волосся", "💇", "hair", "haar"),
    ]),
    "nature": ({"en": "Nature and weather", "nl": "Natuur en weer"}, [
        ("сонце", "☀️", "sun", "zon"), ("місяць", "🌙", "moon", "maan"), ("зірка", "⭐", "star", "ster"),
        ("дощ", "🌧️", "rain", "regen"), ("сніг", "❄️", "snow", "sneeuw"), ("дерево", "🌳", "tree", "boom"),
        ("квітка", "🌸", "flower", "bloem"), ("море", "🌊", "sea", "zee"), ("гора", "⛰️", "mountain", "berg"),
        ("небо", "🌤️", "sky", "lucht"), ("мак", "🌺", "poppy", "klaproos"),
    ]),
    "numbers": ({"en": "Numbers", "nl": "Getallen"}, [
        ("один", "1️⃣", "one", "een"), ("два", "2️⃣", "two", "twee"), ("три", "3️⃣", "three", "drie"),
        ("чотири", "4️⃣", "four", "vier"), ("п'ять", "5️⃣", "five", "vijf"), ("шість", "6️⃣", "six", "zes"),
        ("сім", "7️⃣", "seven", "zeven"), ("вісім", "8️⃣", "eight", "acht"), ("дев'ять", "9️⃣", "nine", "negen"),
        ("десять", "🔟", "ten", "tien"),
    ]),
    "colours": ({"en": "Colours", "nl": "Kleuren"}, [
        ("червоний", "🔴", "red", "rood"), ("синій", "🔵", "blue", "blauw"), ("жовтий", "🟡", "yellow", "geel"),
        ("зелений", "🟢", "green", "groen"), ("чорний", "⚫", "black", "zwart"), ("білий", "⚪", "white", "wit"),
        ("помаранчевий", "🟠", "orange", "oranje"), ("фіолетовий", "🟣", "purple", "paars"),
        ("коричневий", "🟤", "brown", "bruin"),
    ]),
    "basics": ({"en": "Small words", "nl": "Kleine woordjes"}, [
        ("так", "✅", "yes", "ja"), ("ні", "❌", "no", "nee"), ("добре", "👍", "good / okay", "goed / oké"),
        ("там", "👉", "there", "daar"), ("тут", "👇", "here", "hier"), ("кома", "✍️", "comma", "komma"),
    ]),
}
WORDS = {}
for _t, (_n, _list) in THEMES.items():
    for _w, _e, _en, _nl in _list:
        WORDS["w:" + _w] = {"id": "w:" + _w, "uk": _w, "emoji": _e, "en": _en, "nl": _nl, "theme": _t}

# ---------------------------------------------------------------- phrases
PHRASE_CATS = {
    "greet": ({"en": "Hello and goodbye", "nl": "Groeten"}, [
        ("Привіт!", "Hi!", "Hoi!"),
        ("Добрий день!", "Hello! (good day)", "Goedendag!"),
        ("Добрий ранок!", "Good morning!", "Goedemorgen!"),
        ("Добрий вечір!", "Good evening!", "Goedenavond!"),
        ("На добраніч!", "Good night!", "Welterusten!"),
        ("До побачення!", "Goodbye!", "Tot ziens!"),
        ("Бувай!", "Bye!", "Doei!"),
        ("Дякую!", "Thank you!", "Dank je wel!"),
        ("Будь ласка.", "Please. / You're welcome.", "Alsjeblieft. / Graag gedaan."),
        ("Вибачте.", "Sorry. / Excuse me.", "Sorry. / Pardon."),
        ("Ласкаво просимо!", "Welcome!", "Welkom!"),
    ]),
    "talk": ({"en": "Small talk", "nl": "Een praatje"}, [
        ("Як справи?", "How are you?", "Hoe gaat het?"),
        ("Добре, дякую.", "Fine, thank you.", "Goed, dank je."),
        ("Як тебе звати?", "What is your name?", "Hoe heet je?"),
        ("Мене звати Анна.", "My name is Anna.", "Ik heet Anna."),
        ("Я з Нідерландів.", "I am from the Netherlands.", "Ik kom uit Nederland."),
        ("Я вивчаю українську мову.", "I am learning Ukrainian.", "Ik leer Oekraïens."),
        ("Я не розумію.", "I don't understand.", "Ik begrijp het niet."),
        ("Повторіть, будь ласка.", "Please say that again.", "Wilt u dat herhalen, alstublieft?"),
        ("Говоріть повільніше, будь ласка.", "Please speak more slowly.", "Wilt u langzamer praten, alstublieft?"),
        ("Що це?", "What is this?", "Wat is dit?"),
        ("Скільки це коштує?", "How much does it cost?", "Hoeveel kost het?"),
    ]),
    "family": ({"en": "With the family", "nl": "Met de familie"}, [
        ("Я тебе люблю.", "I love you.", "Ik hou van je."),
        ("Я сумую за тобою.", "I miss you.", "Ik mis je."),
        ("Як ти?", "How are you doing?", "Hoe is het met je?"),
        ("Це моя дружина.", "This is my wife.", "Dit is mijn vrouw."),
        ("Це мій син.", "This is my son.", "Dit is mijn zoon."),
        ("Це моя донька.", "This is my daughter.", "Dit is mijn dochter."),
        ("Ми живемо в Нідерландах.", "We live in the Netherlands.", "Wij wonen in Nederland."),
        ("Обіймаю тебе!", "A big hug!", "Een dikke knuffel!"),
        ("Смачного!", "Enjoy your meal!", "Eet smakelijk!"),
        ("Дуже смачно!", "Very tasty!", "Heel lekker!"),
        ("Я хочу їсти.", "I'm hungry.", "Ik heb honger."),
        ("Будьмо!", "Cheers!", "Proost!"),
        ("З днем народження!", "Happy birthday!", "Gefeliciteerd met je verjaardag!"),
    ]),
}
PROPER = {"Анна", "Нідерландів", "Нідерландах", "Україна"}
PHRASES = {}
for _c, (_n, _list) in PHRASE_CATS.items():
    for _i, (_uk, _en, _nl) in enumerate(_list):
        PHRASES[f"p:{_c}:{_i}"] = {"id": f"p:{_c}:{_i}", "uk": _uk, "en": _en, "nl": _nl, "cat": _c}


def words_of(s):
    return re.sub(r"[.,!?]", "", s).split()


def tile(w):
    return w if w in PROPER else w.lower()


def sentence_key(s):
    return " ".join(tile(w) for w in words_of(s))


# ---------------------------------------------------------------- exercises
GROUPS = [
    {"key": "abetka", "icon": "🔤", "title": {"en": "Alphabet", "nl": "Alfabet"},
     "desc": {"en": "The 33 Cyrillic letters, step by step", "nl": "De 33 Cyrillische letters, stap voor stap"},
     "ex": ["a-sound", "a-hear", "a-read"], "focus": [(g, v[0]) for g, v in LETTER_GROUPS.items()]},
    {"key": "slova", "icon": "🍎", "title": {"en": "Words", "nl": "Woorden"},
     "desc": {"en": "Everyday words with pictures", "nl": "Woorden van elke dag, met plaatjes"},
     "ex": ["w-meaning", "w-word", "w-type"], "focus": [(t, v[0]) for t, v in THEMES.items()]},
    {"key": "frazy", "icon": "💬", "title": {"en": "Phrases", "nl": "Zinnetjes"},
     "desc": {"en": "Greetings, small talk and family phrases", "nl": "Groeten, een praatje en zinnetjes voor de familie"},
     "ex": ["p-meaning", "p-build"], "focus": [(c, v[0]) for c, v in PHRASE_CATS.items()]},
    {"key": "sluhaty", "icon": "🎧", "title": {"en": "Listening", "nl": "Luisteren"},
     "desc": {"en": "Hear it and pick the meaning, or write it down", "nl": "Luister en kies de betekenis, of schrijf het op"},
     "ex": ["l-word", "l-phrase", "l-dictee"], "focus": []},
]
EXERCISES = {
    "a-sound": {"en": ("Letter → sound", "Which sound does this letter make?"), "nl": ("Letter → klank", "Welke klank maakt deze letter?")},
    "a-hear": {"en": ("Hear the letter", "Listen and pick the letter."), "nl": ("Hoor de letter", "Luister en kies de letter.")},
    "a-read": {"en": ("Read words", "Read the word: how do you say it?"), "nl": ("Woorden lezen", "Lees het woord: hoe zeg je het?")},
    "w-meaning": {"en": ("What does it mean?", "Pick the meaning."), "nl": ("Wat betekent het?", "Kies de betekenis.")},
    "w-word": {"en": ("Which word?", "Pick the Ukrainian word."), "nl": ("Welk woord?", "Kies het Oekraïense woord.")},
    "w-type": {"en": ("Write the word", "Type it in Cyrillic (keyboard below)."), "nl": ("Schrijf het woord", "Typ het in het Cyrillisch (toetsenbord hieronder).")},
    "p-meaning": {"en": ("What does it mean?", "Pick the meaning."), "nl": ("Wat betekent het?", "Kies de betekenis.")},
    "p-build": {"en": ("Build the phrase", "Tap the words in the right order."), "nl": ("Maak het zinnetje", "Tik de woorden in de goede volgorde.")},
    "l-word": {"en": ("Which word do you hear?", "Listen and pick the meaning."), "nl": ("Welk woord hoor je?", "Luister en kies de betekenis.")},
    "l-phrase": {"en": ("Which phrase do you hear?", "Listen and pick the meaning."), "nl": ("Welk zinnetje hoor je?", "Luister en kies de betekenis.")},
    "l-dictee": {"en": ("Dictation", "Listen and write the word in Cyrillic."), "nl": ("Dictee", "Luister en schrijf het woord in het Cyrillisch.")},
}


def meaning(item, lang):
    return f"{item['emoji']} {item[lang]}" if item.get("emoji") else item[lang]


def letter_label(l):
    return f"{LETTERS[l]['up']} {LETTERS[l]['low']}"


def allowed_letters(focus):
    order = ["g1", "g2", "g3"]
    if focus not in order:
        return set(LETTERS)
    upto = order[:order.index(focus) + 1]
    return {l for g in upto for l in LETTER_GROUPS[g][1]}


def reading_words(focus):
    ok = {l.lower() for l in allowed_letters(focus)} | {"'"}
    words = {w["uk"] for w in WORDS.values()} | {LETTERS[l]["word"].lower() for l in LETTERS}
    return sorted(w for w in words if set(w.lower()) <= ok)


def naive_reading(word):
    """How someone who doesn't know Cyrillic would (wrongly) read the word."""
    out = []
    for ch in word:
        up = ch.upper()
        out.append(LOOKALIKE.get(up, TR.get(ch.lower(), ch)))
    return "".join(out)


def pool(ex, focus, weak):
    if ex in ("a-sound", "a-hear"):
        items = [f"l:{l}" for l in LETTERS if focus in ("alle", "zwak", "") or GROUP_OF[l] == focus]
    elif ex == "a-read":
        items = [f"r:{w}" for w in reading_words(focus if focus in LETTER_GROUPS else "alle")]
    elif ex in ("w-meaning", "w-word", "w-type", "l-word", "l-dictee"):
        items = [i for i, w in WORDS.items() if focus in ("alle", "zwak", "") or w["theme"] == focus]
    else:
        items = [i for i, p in PHRASES.items() if focus in ("alle", "zwak", "") or p["cat"] == focus]
        if ex == "p-build":
            items = [i for i in items if len(words_of(PHRASES[i]["uk"])) >= 2]
    note = None
    if focus == "zwak":
        w = [i for i in items if i in weak]
        if len(w) >= 3:
            items = w
        else:
            note = "no_weak"
    return items, note


def _shuffled(tiles):
    for _ in range(10):
        t = tiles[:]
        random.shuffle(t)
        if t != tiles or len(tiles) < 2:
            return t
    return t


def question(ex, item_id, lang):
    q = {"item": item_id, "ex": ex}
    if item_id.startswith("l:"):
        L = LETTERS[item_id[2:]]
        q["say"] = L["name"]
        q["info"] = {"big": letter_label(L["up"]), "line": f"{L['emoji']} {L['word']} ({translit(L['word'])}) = {L[lang]}",
                     "hint": L["hint_" + lang], "say2": L["word"]}
        if ex == "a-sound":
            distr = {LETTERS[x]["sound"] for x in LETTERS if x != L["up"]} - {L["sound"]}
            if L["up"] in LOOKALIKE:
                distr.discard(LOOKALIKE[L["up"]])
                opts = [LOOKALIKE[L["up"]]] + random.sample(sorted(distr), 3)
            else:
                opts = random.sample(sorted(distr), 4)
            q.update(kind="choice", prompt={"letter": letter_label(L["up"])}, options=opts + [L["sound"]],
                     answer=L["sound"], accepted=[L["sound"]])
        else:  # a-hear
            others = [x for x in LETTERS if x != L["up"]]
            same = [x for x in others if GROUP_OF[x] == GROUP_OF[L["up"]]]
            pick = random.sample(same, min(2, len(same)))
            pick += random.sample([x for x in others if x not in pick], 4 - len(pick))
            q.update(kind="choice", prompt={"say": L["name"], "listen": True}, opt_style="letter",
                     options=[letter_label(x) for x in pick] + [letter_label(L["up"])],
                     answer=letter_label(L["up"]), accepted=[letter_label(L["up"])])
    elif item_id.startswith("r:"):
        w = item_id[2:]
        right = translit(w)
        distr = {naive_reading(w)} - {right}
        others = [x for x in reading_words("alle") if x != w and abs(len(x) - len(w)) <= 2]
        for x in random.sample(others, min(8, len(others))):
            if len(distr) >= 4:
                break
            if translit(x) != right:
                distr.add(translit(x))
        known = next((it for it in WORDS.values() if it["uk"] == w), None) or \
            next(({"emoji": L["emoji"], "en": L["en"], "nl": L["nl"]} for L in LETTERS.values() if L["word"].lower() == w), None)
        q["say"] = w
        q["info"] = {"big": w, "line": f"{w} = {right}" + (f" · {meaning(known, lang)}" if known else "")}
        q.update(kind="choice", prompt={"word": w}, options=list(distr)[:4] + [right], answer=right, accepted=[right])
    elif item_id in WORDS:
        w = WORDS[item_id]
        same = [x for x in WORDS.values() if x["theme"] == w["theme"] and x["id"] != item_id]
        if len(same) < 4:
            same += random.sample([x for x in WORDS.values() if x["id"] != item_id and x not in same], 4 - len(same))
        distr = random.sample(same, 4)
        q["say"] = w["uk"]
        q["info"] = {"big": w["uk"], "translit": translit(w["uk"]), "line": meaning(w, lang)}
        if ex in ("w-meaning", "l-word"):
            prompt = {"word": w["uk"]} if ex == "w-meaning" else {"say": w["uk"], "listen": True}
            q.update(kind="choice", prompt=prompt, options=[meaning(x, lang) for x in distr] + [meaning(w, lang)],
                     answer=meaning(w, lang), accepted=[meaning(w, lang)])
        elif ex == "w-word":
            q.update(kind="choice", prompt={"meaning": meaning(w, lang)}, opt_style="cyr",
                     options=[x["uk"] for x in distr] + [w["uk"]], answer=w["uk"], accepted=[w["uk"]])
        else:  # w-type, l-dictee
            prompt = {"meaning": meaning(w, lang)} if ex == "w-type" else {"say": w["uk"], "listen": True}
            q.update(kind="type", prompt=prompt, answer=w["uk"], accepted=[w["uk"]], keyboard=True)
    else:
        p = PHRASES[item_id]
        q["say"] = p["uk"]
        q["info"] = {"big": p["uk"], "translit": translit(p["uk"]), "line": p[lang]}
        if ex in ("p-meaning", "l-phrase"):
            same = [x for x in PHRASES.values() if x["id"] != item_id]
            distr = random.sample([x for x in same if x["cat"] == p["cat"]], 3) + random.sample(
                [x for x in same if x["cat"] != p["cat"]], 1)
            prompt = {"phrase": p["uk"]} if ex == "p-meaning" else {"say": p["uk"], "listen": True}
            q.update(kind="choice", prompt=prompt, options=[x[lang] for x in distr] + [p[lang]],
                     answer=p[lang], accepted=[p[lang]])
        else:  # p-build
            end = p["uk"][-1] if p["uk"][-1] in ".!?" else ""
            q.update(kind="build", prompt={"meaning": p[lang], "end": end}, tiles=_shuffled([tile(w) for w in words_of(p["uk"])]),
                     answer=p["uk"], accepted=[sentence_key(p["uk"])])
    if "options" in q:
        random.shuffle(q["options"])
        if q.get("opt_style") == "cyr":
            q["opt_translit"] = [translit(o) for o in q["options"]]
    return q


def category(item_id, lang="en"):
    """(group, category) labels for the scores."""
    if item_id.startswith("l:"):
        return ("abetka", GROUP_OF[item_id[2:]])
    if item_id.startswith("r:"):
        return ("abetka", "read")
    if item_id in WORDS:
        return ("slova", WORDS[item_id]["theme"])
    return ("frazy", PHRASES[item_id]["cat"])


CAT_NAMES = {**{g: v[0] for g, v in LETTER_GROUPS.items()}, "read": {"en": "Reading words", "nl": "Woorden lezen"},
             **{t: v[0] for t, v in THEMES.items()}, **{c: v[0] for c, v in PHRASE_CATS.items()}}
GROUP_NAMES = {g["key"]: g["title"] for g in GROUPS}


def item_label(item_id, lang):
    if item_id.startswith("l:"):
        L = LETTERS[item_id[2:]]
        return f"{letter_label(L['up'])} ({L['sound']})", L["name"]
    if item_id.startswith("r:"):
        w = item_id[2:]
        return f"{w} ({translit(w)})", w
    if item_id in WORDS:
        w = WORDS[item_id]
        return f"{w['uk']} ({translit(w['uk'])}) = {meaning(w, lang)}", w["uk"]
    p = PHRASES[item_id]
    return f"{p['uk']} = {p[lang]}", p["uk"]


def all_phrases():
    out = {L["name"] for L in LETTERS.values()} | {L["word"] for L in LETTERS.values()}
    out |= {w["uk"] for w in WORDS.values()} | {p["uk"] for p in PHRASES.values()}
    out |= set(reading_words("alle"))
    return out


def alphabet(lang):
    return [{"up": L["up"], "low": L["low"], "sound": L["sound"], "name": L["name"], "word": L["word"],
             "word_tr": translit(L["word"]), "emoji": L["emoji"], "meaning": L[lang], "hint": L["hint_" + lang],
             "group": GROUP_OF[L["up"]]} for L in LETTERS.values()]
