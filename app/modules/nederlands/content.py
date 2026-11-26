"""Leerstof voor Nederlands (A1-A2): woorden, werkwoorden en zinnen.

Woorden toevoegen: zet ze in WORDS hieronder als  ("woord", "de"/"het", "emoji").
Zinnen toevoegen: zet ze in SENTENCES als  ("Zin.", ["andere goede volgorde.", ...]).
"""
import random
import re

# ======================================================================
# WOORDEN
# ======================================================================
THEMES = {
    "eten": ("Eten en drinken", [
        ("appel", "de", "🍎"), ("banaan", "de", "🍌"), ("brood", "het", "🍞"), ("kaas", "de", "🧀"),
        ("ei", "het", "🥚"), ("melk", "de", "🥛"), ("koffie", "de", "☕"), ("thee", "de", "🍵"),
        ("water", "het", "💧"), ("wijn", "de", "🍷"), ("bier", "het", "🍺"), ("tomaat", "de", "🍅"),
        ("wortel", "de", "🥕"), ("aardappel", "de", "🥔"), ("vlees", "het", "🥩"), ("soep", "de", "🍲"),
        ("taart", "de", "🎂"), ("ijsje", "het", "🍦"), ("druif", "de", "🍇"), ("citroen", "de", "🍋"),
        ("aardbei", "de", "🍓"), ("peer", "de", "🍐"), ("rijst", "de", "🍚"), ("koekje", "het", "🍪"),
        ("boter", "de", "🧈"), ("ui", "de", "🧅"), ("zout", "het", "🧂"), ("pizza", "de", "🍕"),
    ]),
    "huis": ("In huis", [
        ("huis", "het", "🏠"), ("deur", "de", "🚪"), ("bed", "het", "🛏️"), ("stoel", "de", "🪑"),
        ("raam", "het", "🪟"), ("bank", "de", "🛋️"), ("douche", "de", "🚿"), ("bad", "het", "🛁"),
        ("wc", "de", "🚽"), ("sleutel", "de", "🔑"), ("lamp", "de", "💡"), ("klok", "de", "🕰️"),
        ("spiegel", "de", "🪞"), ("kaars", "de", "🕯️"), ("telefoon", "de", "📱"), ("computer", "de", "💻"),
        ("televisie", "de", "📺"), ("boek", "het", "📖"), ("pen", "de", "🖊️"), ("schaar", "de", "✂️"),
        ("mes", "het", "🔪"), ("pan", "de", "🍳"), ("emmer", "de", "🪣"), ("bezem", "de", "🧹"),
        ("zeep", "de", "🧼"),
    ]),
    "mensen": ("Mensen", [
        ("man", "de", "👨"), ("vrouw", "de", "👩"), ("jongen", "de", "👦"), ("meisje", "het", "👧"),
        ("baby", "de", "👶"), ("opa", "de", "👴"), ("oma", "de", "👵"), ("dokter", "de", "👩‍⚕️"),
        ("politieagent", "de", "👮"), ("kok", "de", "🧑‍🍳"), ("leraar", "de", "🧑‍🏫"), ("boer", "de", "🧑‍🌾"),
        ("gezin", "het", "👨‍👩‍👧"), ("koning", "de", "🤴"),
    ]),
    "lichaam": ("Het lichaam", [
        ("oog", "het", "👁️"), ("oor", "het", "👂"), ("neus", "de", "👃"), ("mond", "de", "👄"),
        ("tand", "de", "🦷"), ("hand", "de", "✋"), ("voet", "de", "🦶"), ("been", "het", "🦵"),
        ("arm", "de", "💪"), ("hart", "het", "❤️"), ("tong", "de", "👅"), ("bot", "het", "🦴"),
    ]),
    "kleding": ("Kleding", [
        ("jas", "de", "🧥"), ("broek", "de", "👖"), ("shirt", "het", "👕"), ("jurk", "de", "👗"),
        ("schoen", "de", "👟"), ("hoed", "de", "🎩"), ("pet", "de", "🧢"), ("sok", "de", "🧦"),
        ("handschoen", "de", "🧤"), ("sjaal", "de", "🧣"), ("bril", "de", "👓"), ("tas", "de", "👜"),
        ("horloge", "het", "⌚"), ("ring", "de", "💍"), ("paraplu", "de", "☂️"),
    ]),
    "dieren": ("Dieren", [
        ("hond", "de", "🐕"), ("kat", "de", "🐈"), ("paard", "het", "🐎"), ("koe", "de", "🐄"),
        ("varken", "het", "🐖"), ("schaap", "het", "🐑"), ("kip", "de", "🐔"), ("vogel", "de", "🐦"),
        ("vis", "de", "🐟"), ("muis", "de", "🐭"), ("konijn", "het", "🐇"), ("eend", "de", "🦆"),
        ("olifant", "de", "🐘"), ("leeuw", "de", "🦁"), ("beer", "de", "🐻"), ("slang", "de", "🐍"),
        ("vlinder", "de", "🦋"), ("bij", "de", "🐝"), ("spin", "de", "🕷️"), ("aap", "de", "🐒"),
    ]),
    "stad": ("Stad en vervoer", [
        ("auto", "de", "🚗"), ("fiets", "de", "🚲"), ("bus", "de", "🚌"), ("trein", "de", "🚆"),
        ("vliegtuig", "het", "✈️"), ("boot", "de", "⛵"), ("taxi", "de", "🚕"), ("ziekenhuis", "het", "🏥"),
        ("school", "de", "🏫"), ("kerk", "de", "⛪"), ("station", "het", "🚉"), ("winkel", "de", "🏪"),
        ("hotel", "het", "🏨"), ("geld", "het", "💶"), ("brief", "de", "✉️"), ("stoplicht", "het", "🚦"),
        ("brug", "de", "🌉"), ("vrachtwagen", "de", "🚚"),
    ]),
    "natuur": ("Natuur en weer", [
        ("zon", "de", "☀️"), ("maan", "de", "🌙"), ("ster", "de", "⭐"), ("regen", "de", "🌧️"),
        ("sneeuw", "de", "❄️"), ("wolk", "de", "☁️"), ("boom", "de", "🌳"), ("bloem", "de", "🌸"),
        ("zee", "de", "🌊"), ("berg", "de", "⛰️"), ("vuur", "het", "🔥"), ("regenboog", "de", "🌈"),
        ("paddenstoel", "de", "🍄"), ("blad", "het", "🍁"),
    ]),
    "vrijetijd": ("Vrije tijd", [
        ("bal", "de", "⚽"), ("gitaar", "de", "🎸"), ("film", "de", "🎬"), ("muziek", "de", "🎵"),
        ("cadeau", "het", "🎁"), ("feest", "het", "🎉"), ("kalender", "de", "📅"), ("camera", "de", "📷"),
        ("krant", "de", "📰"), ("wekker", "de", "⏰"), ("piano", "de", "🎹"), ("tent", "de", "⛺"),
    ]),
}
WORDS = {}
for _t, (_name, _list) in THEMES.items():
    for _w, _a, _e in _list:
        WORDS["w:" + _w] = {"id": "w:" + _w, "word": _w, "art": _a, "emoji": _e, "theme": _t}


def word_say(w):
    return f"{w['art']} {w['word']}"


# ======================================================================
# WERKWOORDEN
# ======================================================================
PERSONS = ["ik", "jij", "u", "hij", "zij", "wij", "jullie", "zij (mv)"]
PLURAL = {"wij", "jullie", "zij (mv)"}

# inf: (ik-vorm, verleden enkelvoud, verleden meervoud, voltooid deelwoord of None, hulpww, soort)
# soort: zh = zijn/hebben, zwak = regelmatig (werkte), sterk = onregelmatig (liep), modaal
VERBS = {
    "zijn": ("ben", "was", "waren", "geweest", "zijn", "zh"),
    "hebben": ("heb", "had", "hadden", "gehad", "hebben", "zh"),
    # zwak
    "werken": ("werk", "werkte", "werkten", "gewerkt", "hebben", "zwak"),
    "wonen": ("woon", "woonde", "woonden", "gewoond", "hebben", "zwak"),
    "maken": ("maak", "maakte", "maakten", "gemaakt", "hebben", "zwak"),
    "spelen": ("speel", "speelde", "speelden", "gespeeld", "hebben", "zwak"),
    "koken": ("kook", "kookte", "kookten", "gekookt", "hebben", "zwak"),
    "praten": ("praat", "praatte", "praatten", "gepraat", "hebben", "zwak"),
    "fietsen": ("fiets", "fietste", "fietsten", "gefietst", "hebben", "zwak"),
    "leren": ("leer", "leerde", "leerden", "geleerd", "hebben", "zwak"),
    "wachten": ("wacht", "wachtte", "wachtten", "gewacht", "hebben", "zwak"),
    "betalen": ("betaal", "betaalde", "betaalden", "betaald", "hebben", "zwak"),
    "luisteren": ("luister", "luisterde", "luisterden", "geluisterd", "hebben", "zwak"),
    "dansen": ("dans", "danste", "dansten", "gedanst", "hebben", "zwak"),
    "bellen": ("bel", "belde", "belden", "gebeld", "hebben", "zwak"),
    "reizen": ("reis", "reisde", "reisden", "gereisd", "hebben", "zwak"),
    "stoppen": ("stop", "stopte", "stopten", "gestopt", "hebben", "zwak"),
    "huren": ("huur", "huurde", "huurden", "gehuurd", "hebben", "zwak"),
    "antwoorden": ("antwoord", "antwoordde", "antwoordden", "geantwoord", "hebben", "zwak"),
    "trouwen": ("trouw", "trouwde", "trouwden", "getrouwd", "zijn", "zwak"),
    # sterk / onregelmatig
    "gaan": ("ga", "ging", "gingen", "gegaan", "zijn", "sterk"),
    "komen": ("kom", "kwam", "kwamen", "gekomen", "zijn", "sterk"),
    "blijven": ("blijf", "bleef", "bleven", "gebleven", "zijn", "sterk"),
    "doen": ("doe", "deed", "deden", "gedaan", "hebben", "sterk"),
    "zien": ("zie", "zag", "zagen", "gezien", "hebben", "sterk"),
    "staan": ("sta", "stond", "stonden", "gestaan", "hebben", "sterk"),
    "lopen": ("loop", "liep", "liepen", "gelopen", "hebben", "sterk"),
    "eten": ("eet", "at", "aten", "gegeten", "hebben", "sterk"),
    "drinken": ("drink", "dronk", "dronken", "gedronken", "hebben", "sterk"),
    "slapen": ("slaap", "sliep", "sliepen", "geslapen", "hebben", "sterk"),
    "lezen": ("lees", "las", "lazen", "gelezen", "hebben", "sterk"),
    "schrijven": ("schrijf", "schreef", "schreven", "geschreven", "hebben", "sterk"),
    "kijken": ("kijk", "keek", "keken", "gekeken", "hebben", "sterk"),
    "kopen": ("koop", "kocht", "kochten", "gekocht", "hebben", "sterk"),
    "zitten": ("zit", "zat", "zaten", "gezeten", "hebben", "sterk"),
    "geven": ("geef", "gaf", "gaven", "gegeven", "hebben", "sterk"),
    "nemen": ("neem", "nam", "namen", "genomen", "hebben", "sterk"),
    "spreken": ("spreek", "sprak", "spraken", "gesproken", "hebben", "sterk"),
    "vinden": ("vind", "vond", "vonden", "gevonden", "hebben", "sterk"),
    "krijgen": ("krijg", "kreeg", "kregen", "gekregen", "hebben", "sterk"),
    "weten": ("weet", "wist", "wisten", "geweten", "hebben", "sterk"),
    # modaal
    "kunnen": ("kan", "kon", "konden", None, "hebben", "modaal"),
    "willen": ("wil", "wilde", "wilden", None, "hebben", "modaal"),
    "mogen": ("mag", "mocht", "mochten", None, "hebben", "modaal"),
    "moeten": ("moet", "moest", "moesten", None, "hebben", "modaal"),
    "zullen": ("zal", "zou", "zouden", None, "hebben", "modaal"),
}
# Afwijkende tegenwoordige tijd: persoon -> [goede vormen]. Eerste vorm = standaard.
PRESENT_SPECIAL = {
    "zijn": {"ik": ["ben"], "jij": ["bent"], "u": ["bent"], "hij": ["is"], "zij": ["is"]},
    "hebben": {"ik": ["heb"], "jij": ["hebt"], "u": ["hebt", "heeft"], "hij": ["heeft"], "zij": ["heeft"]},
    "kunnen": {"ik": ["kan"], "jij": ["kunt", "kan"], "u": ["kunt", "kan"], "hij": ["kan"], "zij": ["kan"]},
    "willen": {"ik": ["wil"], "jij": ["wilt", "wil"], "u": ["wilt", "wil"], "hij": ["wil"], "zij": ["wil"]},
    "zullen": {"ik": ["zal"], "jij": ["zult", "zal"], "u": ["zult", "zal"], "hij": ["zal"], "zij": ["zal"]},
    "gaan": {"ik": ["ga"], "jij": ["gaat"], "u": ["gaat"], "hij": ["gaat"], "zij": ["gaat"]},
    "doen": {"ik": ["doe"], "jij": ["doet"], "u": ["doet"], "hij": ["doet"], "zij": ["doet"]},
    "zien": {"ik": ["zie"], "jij": ["ziet"], "u": ["ziet"], "hij": ["ziet"], "zij": ["ziet"]},
    "staan": {"ik": ["sta"], "jij": ["staat"], "u": ["staat"], "hij": ["staat"], "zij": ["staat"]},
    "mogen": {"ik": ["mag"], "jij": ["mag"], "u": ["mag"], "hij": ["mag"], "zij": ["mag"]},
}
IRREGULAR_NOW = ["gaan", "doen", "zien", "staan", "kunnen", "willen", "mogen", "moeten", "zullen"]
WOU = {"willen": ("wou", "wouden")}  # spreektaal, ook goed


def present(inf, person):
    if person in PLURAL:
        return [inf]
    sp = PRESENT_SPECIAL.get(inf, {})
    if person in sp:
        return sp[person]
    stem = VERBS[inf][0]
    if person == "ik":
        return [stem]
    return [stem if stem.endswith("t") else stem + "t"]


def past(inf, person):
    v = VERBS[inf]
    forms = [v[2]] if person in PLURAL else [v[1]]
    if inf in WOU:
        forms.append(WOU[inf][1 if person in PLURAL else 0])
    return forms


def aux_forms(inf, person):
    aux = VERBS[inf][4]
    if inf == "lopen":
        return present("hebben", person) + present("zijn", person)
    return present(aux, person)


def perfect(inf, person):
    return [f"{a} {VERBS[inf][3]}" for a in aux_forms(inf, person)]


TENSES = {"nu": ("tegenwoordige tijd", present), "verl": ("verleden tijd", past), "volt": ("voltooide tijd", perfect)}

VERB_LEVELS = [
    ("1", "Zijn en hebben", "ik ben, jij hebt …", [(v, "nu") for v in ("zijn", "hebben")]),
    ("2", "Regelmatig (nu)", "ik werk, jij werkt, wij werken", [(v, "nu") for v in VERBS if v not in IRREGULAR_NOW and VERBS[v][5] != "zh"]),
    ("3", "Onregelmatig (nu)", "ik ga, jij kunt, hij mag …", [(v, "nu") for v in IRREGULAR_NOW]),
    ("4", "Verleden tijd: regelmatig", "ik werkte, wij woonden", [(v, "verl") for v in VERBS if VERBS[v][5] == "zwak"]),
    ("5", "Verleden tijd: onregelmatig", "ik was, ik liep, wij gingen", [(v, "verl") for v in VERBS if VERBS[v][5] != "zwak"]),
    ("6", "Voltooide tijd", "ik heb gewerkt, ik ben gegaan", [(v, "volt") for v in VERBS if VERBS[v][3]]),
]
VERB_ITEMS = {}
for _lv in VERB_LEVELS:
    for _v, _t in _lv[3]:
        for _p in PERSONS:
            _id = f"v:{_v}:{_t}:{_p}"
            VERB_ITEMS[_id] = {"id": _id, "verb": _v, "tense": _t, "person": _p, "level": _lv[0]}


def verb_forms(item):
    return TENSES[item["tense"]][1](item["verb"], item["person"])


def verb_say(item):
    return f"{item['person'].replace(' (mv)', '')} {verb_forms(item)[0]}"


def _verb_distractors(item):
    v, p, t = item["verb"], item["person"], item["tense"]
    ok = set(verb_forms(item))
    pool = set()
    for q in PERSONS:
        pool.update(present(v, q))
        pool.update(past(v, q))
    data = VERBS[v]
    if t == "volt":
        pool = set()
        part = data[3]
        for a in ("hebben", "zijn"):
            pool.update(f"{x} {part}" for x in present(a, p))
        if part.endswith("t"):
            pool.add(f"{aux_forms(v, p)[0]} {part[:-1]}d")
        elif part.endswith("d"):
            pool.add(f"{aux_forms(v, p)[0]} {part[:-1]}t")
        if data[5] == "sterk":
            pool.add(f"{aux_forms(v, p)[0]} ge{data[0]}d")
        for q in PERSONS:
            pool.update(f"{x} {part}" for x in present(data[4], q))
    else:
        stem = data[0]
        if data[5] == "zwak":
            wrong = "de" if data[1].endswith("te") else "te"
            pool.add(stem + wrong)
            pool.add(stem + wrong + "n")
        if stem.endswith("d"):
            pool.add(stem + "t")
        if data[5] == "sterk":
            pool.add(stem + "de")
        if data[3]:
            pool.add(data[3])
    pool -= ok
    return [x for x in pool if x]


# ======================================================================
# ZINNEN
# ======================================================================
SENT_CATS = {
    "gewoon": ("Gewone zinnen", [
        ("Ik woon in Utrecht.", []),
        ("Mijn naam is Anna.", []),
        ("Wij eten om zes uur.", ["Om zes uur eten wij."]),
        ("Hij werkt in een winkel.", []),
        ("De kinderen spelen in de tuin.", ["In de tuin spelen de kinderen."]),
        ("Ik drink elke ochtend koffie.", ["Elke ochtend drink ik koffie."]),
        ("Zij leest een boek.", []),
        ("Jullie fietsen naar school.", []),
        ("Het weer is vandaag mooi.", ["Vandaag is het weer mooi."]),
    ]),
    "vragen": ("Vragen", [
        ("Waar woon jij?", []),
        ("Hoe heet jij?", []),
        ("Wat drink jij?", []),
        ("Spreek jij Nederlands?", []),
        ("Hoe laat is het?", []),
        ("Heb jij een broer?", []),
        ("Waar is het station?", []),
        ("Hoeveel kost dit?", []),
    ]),
    "inversie": ("Tijd of plaats vooraan", [
        ("Morgen ga ik naar de markt.", ["Ik ga morgen naar de markt."]),
        ("Vandaag werk ik thuis.", ["Ik werk vandaag thuis."]),
        ("In de zomer fietsen wij veel.", ["Wij fietsen in de zomer veel.", "Wij fietsen veel in de zomer."]),
        ("Om acht uur kijk ik televisie.", ["Ik kijk om acht uur televisie."]),
        ("Op zaterdag doe ik boodschappen.", ["Ik doe op zaterdag boodschappen.", "Ik doe boodschappen op zaterdag."]),
        ("Gisteren was het koud.", ["Het was gisteren koud."]),
    ]),
    "ontkenning": ("Niet en geen", [
        ("Hij heeft geen auto.", []),
        ("Wij hebben geen tijd.", []),
        ("Ik drink geen koffie.", []),
        ("Het is niet ver.", []),
        ("Zij komt vandaag niet.", ["Vandaag komt zij niet."]),
        ("Ik begrijp het niet.", []),
    ]),
    "modaal": ("Kunnen, willen, moeten", [
        ("Ik wil Nederlands leren.", []),
        ("Kun jij mij helpen?", []),
        ("Wij moeten morgen werken.", ["Morgen moeten wij werken."]),
        ("Mag ik iets vragen?", []),
        ("Zij kan goed koken.", []),
        ("Ik wil een kopje thee.", []),
    ]),
    "voltooid": ("Voltooide tijd", [
        ("Ik heb gisteren gewerkt.", ["Gisteren heb ik gewerkt."]),
        ("Wij zijn naar Amsterdam gegaan.", []),
        ("Heb jij het boek gelezen?", []),
        ("Hij heeft een fiets gekocht.", []),
        ("Zij is thuis gebleven.", []),
        ("Ik heb mijn sleutel verloren.", []),
    ]),
    "bijzin": ("Bijzinnen", [
        ("Ik blijf thuis, omdat ik ziek ben.", ["Omdat ik ziek ben, blijf ik thuis."]),
        ("Ik denk dat het gaat regenen.", ["Ik denk dat het regenen gaat."]),
        ("Als het mooi weer is, gaan wij naar het strand.", ["Wij gaan naar het strand als het mooi weer is."]),
        ("Ik weet niet waar hij woont.", []),
        ("Zij leert Nederlands, omdat zij hier woont.", ["Omdat zij hier woont, leert zij Nederlands."]),
        ("Ik bel jou als ik thuis ben.", ["Als ik thuis ben, bel ik jou."]),
    ]),
}
PROPER = {"Utrecht", "Anna", "Amsterdam", "Nederlands"}
SENTS = {}
for _c, (_name, _list) in SENT_CATS.items():
    for _i, (_s, _alts) in enumerate(_list):
        _id = f"s:{_c}:{_i}"
        SENTS[_id] = {"id": _id, "text": _s, "alts": _alts, "cat": _c}


def words_of(sentence):
    return [w for w in re.sub(r"[.,?!]", "", sentence).split()]


def tile(w):
    return w if w in PROPER else w.lower()


def sentence_key(s):
    return " ".join(tile(w) for w in words_of(s))


# ======================================================================
# OEFENINGEN
# ======================================================================
GROUPS = [
    {"key": "woorden", "name": "Woorden", "icon": "🍎", "desc": "Plaatjes, woorden en de of het",
     "ex": [("w-wat", "Wat is dit?", "Kies het goede woord bij het plaatje."),
            ("w-dehet", "De of het?", "Kies het goede lidwoord."),
            ("w-schrijf", "Schrijf het woord", "Typ het woord bij het plaatje.")],
     "focus": [(k, v[0]) for k, v in THEMES.items()]},
    {"key": "werkwoorden", "name": "Werkwoorden", "icon": "🏃", "desc": "ik werk, ik werkte, ik heb gewerkt",
     "ex": [("v-kies", "Kies de vorm", "Kies de goede vorm van het werkwoord."),
            ("v-schrijf", "Schrijf de vorm", "Typ de goede vorm van het werkwoord.")],
     "focus": [(lv[0], f"{lv[0]}. {lv[1]}") for lv in VERB_LEVELS]},
    {"key": "zinnen", "name": "Zinnen", "icon": "🧩", "desc": "Zet de woorden in de goede volgorde",
     "ex": [("z-bouw", "Zinnen maken", "Tik de woorden in de goede volgorde.")],
     "focus": [(k, v[0]) for k, v in SENT_CATS.items()]},
    {"key": "luisteren", "name": "Luisteren", "icon": "🎧", "desc": "Hoor het en kies, schrijf of bouw",
     "ex": [("l-woord", "Welk plaatje?", "Luister en kies het goede plaatje."),
            ("l-dictee", "Woorddictee", "Luister en schrijf het woord."),
            ("l-zin", "Zinnen luisteren", "Luister en zet de woorden in de goede volgorde.")],
     "focus": []},
]
EXERCISES = {e[0]: {"group": g["key"], "name": e[1], "desc": e[2]} for g in GROUPS for e in g["ex"]}


def item_label(item_id):
    """Korte omschrijving voor scorelijsten."""
    if item_id in WORDS:
        w = WORDS[item_id]
        return f"{w['emoji']} {word_say(w)}", word_say(w)
    if item_id in VERB_ITEMS:
        it = VERB_ITEMS[item_id]
        return f"{verb_say(it)} ({it['verb']}, {TENSES[it['tense']][0]})", verb_say(it)
    if item_id in SENTS:
        return SENTS[item_id]["text"], SENTS[item_id]["text"]
    return item_id, ""


def category(item_id):
    if item_id in WORDS:
        return "Woorden", THEMES[WORDS[item_id]["theme"]][0]
    if item_id in VERB_ITEMS:
        lv = VERB_ITEMS[item_id]["level"]
        return "Werkwoorden", next(f"{x[0]}. {x[1]}" for x in VERB_LEVELS if x[0] == lv)
    if item_id in SENTS:
        return "Zinnen", SENT_CATS[SENTS[item_id]["cat"]][0]
    return "", ""


def pool(ex, focus, weak):
    grp = EXERCISES[ex]["group"]
    if ex in ("w-wat", "w-dehet", "w-schrijf", "l-woord", "l-dictee"):
        items = [i for i, w in WORDS.items() if focus in ("alle", "zwak", "") or w["theme"] == focus]
    elif grp == "werkwoorden":
        items = [i for i, v in VERB_ITEMS.items() if focus in ("alle", "zwak", "") or v["level"] == focus]
    else:
        items = [i for i, s in SENTS.items() if focus in ("alle", "zwak", "") or s["cat"] == focus]
    note = None
    if focus == "zwak":
        w = [i for i in items if i in weak]
        if len(w) >= 3:
            items = w
        else:
            note = "Je hebt hier nog geen zwakke punten. Goed bezig! We oefenen alles."
    return items, note


def _shuffled_tiles(words):
    tiles = [tile(w) for w in words]
    for _ in range(10):
        t = tiles[:]
        random.shuffle(t)
        if t != tiles or len(tiles) < 2:
            return t
    return t


def question(ex, item_id):
    q = {"item": item_id, "ex": ex}
    if item_id in WORDS:
        w = WORDS[item_id]
        same = [x for x in WORDS.values() if x["theme"] == w["theme"] and x["id"] != item_id]
        q["say"] = word_say(w)
        q["info"] = {"emoji": w["emoji"], "line": word_say(w)}
        if ex == "w-wat":
            q.update(kind="choice", prompt={"emoji": w["emoji"], "text": "Wat is dit?"}, answer=w["word"], accepted=[w["word"]])
            q["options"] = random.sample([x["word"] for x in same], 4) + [w["word"]]
        elif ex == "w-dehet":
            q.update(kind="choice", prompt={"emoji": w["emoji"], "big": f"… {w['word']}", "say": w["word"]},
                     answer=w["art"], accepted=[w["art"]], options=["de", "het"], keep_order=True)
        elif ex == "w-schrijf":
            q.update(kind="type", prompt={"emoji": w["emoji"], "text": "Schrijf het woord (met de of het mag ook)."},
                     answer=word_say(w), accepted=[w["word"], word_say(w)])
        elif ex == "l-woord":
            q.update(kind="choice", prompt={"say": word_say(w), "listen": True, "text": "Welk plaatje hoor je?"},
                     answer=w["emoji"], accepted=[w["emoji"]], opt_style="emoji")
            q["options"] = [x["emoji"] for x in random.sample(same, 4)] + [w["emoji"]]
        elif ex == "l-dictee":
            q.update(kind="type", prompt={"say": word_say(w), "listen": True, "text": "Schrijf het woord dat je hoort."},
                     answer=word_say(w), accepted=[w["word"], word_say(w)])
    elif item_id in VERB_ITEMS:
        it = VERB_ITEMS[item_id]
        forms = verb_forms(it)
        blanks = "___ ___" if it["tense"] == "volt" else "___"
        hint = {"nu": "nu", "verl": "gisteren (verleden tijd)", "volt": "voltooide tijd"}[it["tense"]]
        q["say"] = verb_say(it)
        q["prompt"] = {"big": f"{it['person']} {blanks}", "sub": f"({it['verb']})", "text": hint, "say_hint": it["verb"]}
        q["answer"] = forms[0]
        q["accepted"] = forms + [f"{it['person'].replace(' (mv)', '')} {f}" for f in forms]
        q["info"] = {"line": verb_say(it), "rows": verb_table(it)}
        if ex == "v-kies":
            d = _verb_distractors(it)
            q.update(kind="choice", options=random.sample(d, min(4, len(d))) + [forms[0]])
        else:
            q.update(kind="type")
    else:
        s = SENTS[item_id]
        q["say"] = s["text"]
        q["info"] = {"line": s["text"]}
        q["kind"] = "build"
        q["tiles"] = _shuffled_tiles(words_of(s["text"]))
        q["answer"] = s["text"]
        q["accepted"] = [sentence_key(s["text"])] + [sentence_key(a) for a in s["alts"]]
        end = "?" if s["text"].endswith("?") else "."
        if ex == "l-zin":
            q["prompt"] = {"say": s["text"], "listen": True, "text": "Luister en maak de zin.", "end": end}
        else:
            q["prompt"] = {"text": "Maak een goede zin.", "end": end, "cat": SENT_CATS[s["cat"]][0]}
    if "options" in q and not q.get("keep_order"):
        random.shuffle(q["options"])
    return q


def verb_table(it):
    v, t = it["verb"], it["tense"]
    rows = []
    for p in ["ik", "jij", "u", "hij", "zij", "wij", "jullie", "zij (mv)"]:
        f = TENSES[t][1](v, p)
        rows.append({"pron": p, "form": " / ".join(f), "hl": p == it["person"]})
    return {"verb": v, "nl": TENSES[t][0], "rows": rows}


def all_phrases():
    out = set()
    for w in WORDS.values():
        out.add(word_say(w))
        out.add(w["word"])
    for it in VERB_ITEMS.values():
        out.add(verb_say(it))
        out.add(it["verb"])
    for s in SENTS.values():
        out.add(s["text"])
    return out
