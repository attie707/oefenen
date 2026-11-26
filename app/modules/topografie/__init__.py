"""Topografie Europa (Dutch): 45 countries, numbered like the school worksheet 'Landen in Europa [1]'."""
import random
import re

import engine as E
from engine import ApiError

KEY = "topografie"
ICON = "🗺️"
TITLE = {"en": "Topography Europe", "nl": "Topografie Europa"}
DESC = {"en": "The 45 countries of Europe: find them on the map and name them",
        "nl": "De 45 landen van Europa: aanwijzen op de kaart en de naam weten"}
TTS_LANG, TTS_AZURE, TTS_PIPER = None, None, None   # no sound in this subject

# number on the worksheet: (name, other accepted spellings)
COUNTRIES = {
    1: ("IJsland", ["Ijsland"]), 2: ("Noorwegen", []), 3: ("Zweden", []), 4: ("Finland", []), 5: ("Ierland", []),
    6: ("Noord-Ierland", []), 7: ("Schotland", []), 8: ("Engeland", []), 9: ("Wales", []), 10: ("Denemarken", []),
    11: ("Estland", []), 12: ("Letland", []), 13: ("Litouwen", []), 14: ("Rusland", []), 15: ("Nederland", ["Holland"]),
    16: ("België", []), 17: ("Luxemburg", []), 18: ("Duitsland", []), 19: ("Polen", []),
    20: ("Wit-Rusland", ["Witrusland", "Belarus"]), 21: ("Tsjechië", ["Tsjechische Republiek"]), 22: ("Frankrijk", []),
    23: ("Zwitserland", []), 24: ("Oostenrijk", []), 25: ("Slowakije", []), 26: ("Oekraïne", []), 27: ("Italië", []),
    28: ("Slovenië", []), 29: ("Kroatië", []), 30: ("Hongarije", []), 31: ("Moldavië", ["Moldova"]), 32: ("Roemenië", []),
    33: ("Bosnië en Herzegovina", ["Bosnië-Herzegovina", "Bosnië", "Bosnië en Herzegowina"]), 34: ("Servië", []),
    35: ("Montenegro", []), 36: ("Kosovo", []), 37: ("Bulgarije", []), 38: ("Albanië", []),
    39: ("Macedonië", ["Noord-Macedonië"]), 40: ("Griekenland", []), 41: ("Turkije", []), 42: ("Portugal", []),
    43: ("Spanje", []), 44: ("Malta", []), 45: ("Cyprus", []),
}
REGIONS = {
    "noord": ("Noord-Europa", [1, 2, 3, 4, 10, 11, 12, 13]),
    "west": ("Britse eilanden en West-Europa", [5, 6, 7, 8, 9, 15, 16, 17, 22]),
    "midden": ("Midden-Europa", [18, 19, 21, 23, 24, 25, 28, 30]),
    "oost": ("Oost-Europa", [14, 20, 26, 31, 32, 37]),
    "balkan": ("De Balkan", [29, 33, 34, 35, 36, 38, 39, 40]),
    "zuid": ("Zuid-Europa", [27, 41, 42, 43, 44, 45]),
}
REGION_OF = {n: k for k, (_, ns) in REGIONS.items() for n in ns}
EXERCISES = {
    "t-waar": ("Stap 1 · Waar ligt het?", "Je krijgt een land. Tik het aan op de kaart."),
    "t-welk": ("Stap 2 · Welk land is dit?", "Een land licht op. Kies de goede naam."),
    "t-nummer": ("Stap 3 · Welk nummer?", "Net als op het werkblad: zoek het nummer bij het land."),
    "t-schrijf": ("Stap 4 · Schrijf het land", "Een land licht op. Typ zelf de naam."),
    "t-toets": ("Proeftoets", "20 vragen door elkaar, met een cijfer aan het eind."),
}
MODE_NAMES = {k: v[0] for k, v in EXERCISES.items()}


def phrases():
    return {name for name, _ in COUNTRIES.values()}


def simple(s):
    s = E.normalize(s).replace("-", " ")
    return re.sub(r"\s+", " ", s)


def check(given, q):
    if q["kind"] in ("click", "number"):
        return 2 if (given or "").strip() == str(q["num"]) else 0
    name, alts = COUNTRIES[q["num"]]
    g = simple(given)
    ok = [simple(x) for x in [name] + alts]
    if g in ok:
        return 2
    if E.strip_accents(g) in [E.strip_accents(x) for x in ok]:
        return 1
    return 0


def handle(action, ctx):
    con, me = ctx.con, ctx.me
    uid = me["id"]

    if action == "home":
        mu = E.module_user(con, uid, KEY)
        steps = {}
        for ex in EXERCISES:
            rows = con.execute("SELECT result FROM answers WHERE user_id=? AND module=? AND mode=? ORDER BY id DESC LIMIT 20",
                               (uid, KEY, ex)).fetchall()
            steps[ex] = {"n": len(rows), "pct": round(50 * sum(r["result"] for r in rows) / len(rows)) if rows else None}
        known = con.execute("SELECT COUNT(DISTINCT substr(key, instr(key, ':') + 1)) FROM progress "
                            "WHERE user_id=? AND module=? AND key LIKE 't-schrijf:%' AND box>=3", (uid, KEY)).fetchone()[0]
        return {"name": me["name"], "xp": mu["xp"], "streak": E.streak(con, uid, KEY), "today": E.today_count(con, uid, KEY),
                "goal": E.DAILY_GOAL, "exercises": [{"key": k, "name": v[0], "desc": v[1], **steps[k]} for k, v in EXERCISES.items()],
                "regions": [{"key": k, "name": v[0], "nums": v[1]} for k, v in REGIONS.items()],
                "known": known, "total": len(COUNTRIES), "best": mu["best"],
                "weak_count": len({k.split(":", 1)[1] for k in E.weak_keys(con, uid, KEY)})}

    if action == "question":
        b = ctx.body()
        ex, focus = b.get("ex"), b.get("focus") or "alle"
        if ex not in EXERCISES:
            raise ApiError(400, "Onbekende oefening")
        note = None
        if focus in REGIONS:
            pool = REGIONS[focus][1]
        elif focus == "zwak":
            weak = {int(k.split(":", 1)[1]) for k in E.weak_keys(con, uid, KEY)}
            pool = sorted(weak)
            if len(pool) < 3:
                pool, note = list(COUNTRIES), "Je hebt (nog) geen moeilijke landen. Knap! We doen alles."
        else:
            pool = list(COUNTRIES)
        kind_ex = random.choice(["t-waar", "t-nummer", "t-schrijf"]) if ex == "t-toets" else ex
        num = int(E.pick_item(con, uid, KEY, kind_ex, [str(n) for n in pool]))
        name = COUNTRIES[num][0]
        region = REGION_OF[num]
        q = {"num": num, "item": str(num), "ex": ex, "kind_ex": kind_ex, "say": name}
        if kind_ex == "t-waar":
            q["kind"] = "click"
            q["prompt"] = {"text": "Waar ligt", "big": name, "view": focus if focus in REGIONS else region}
        elif kind_ex == "t-nummer":
            q["kind"] = "number"
            q["prompt"] = {"text": "Welk nummer hoort bij", "big": name, "numbers": True,
                           "view": focus if focus in REGIONS else region}
        elif kind_ex == "t-welk":
            same = [n for n in REGIONS[region][1] if n != num]
            others = [n for n in COUNTRIES if n != num and n not in same]
            distr = random.sample(same, min(3, len(same)))
            distr += random.sample(others, 4 - len(distr))
            opts = [COUNTRIES[n][0] for n in distr] + [name]
            random.shuffle(opts)
            q["kind"] = "choice"
            q["options"] = opts
            q["prompt"] = {"text": "Welk land is dit?", "highlight": num, "view": focus if focus in REGIONS else region}
        else:
            q["kind"] = "type"
            q["prompt"] = {"text": "Welk land is dit? Typ de naam.", "highlight": num, "view": focus if focus in REGIONS else region}
        qid = E.store_question(q, uid, KEY)
        return {"qid": qid, "ex": ex, "kind": q["kind"], "prompt": q["prompt"], "options": q.get("options"), "note": note}

    if action == "answer":
        b = ctx.body()
        q = E.take_question(b.get("qid"), uid, KEY, "Vraag verlopen, we gaan door met een nieuwe")
        given = (b.get("answer") or "")[:60]
        result = check(given, q)
        E.update_box(con, uid, KEY, f"{q['kind_ex']}:{q['item']}", result)
        name = COUNTRIES[q["num"]][0]
        shown = given
        if q["kind"] == "click" and given.isdigit() and int(given) in COUNTRIES:
            shown = COUNTRIES[int(given)][0]
        E.record_answer(con, uid, KEY, q["kind_ex"], None, q["item"], REGIONS[REGION_OF[q["num"]]][0], name,
                        f'{EXERCISES[q["kind_ex"]][0]}: {name if q["kind"] in ("click", "number") else "nr. " + str(q["num"])}',
                        shown, f"{name} ({q['num']})", result)
        xp = {2: E.XP_CORRECT, 1: E.XP_ALMOST, 0: 0}[result]
        E.add_xp(con, uid, KEY, xp)
        return {"result": ["wrong", "almost", "correct"][result], "num": q["num"], "name": name, "say": name,
                "given": given, "xp_gained": xp, "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL}

    if action == "toets/finish":
        b = ctx.body()
        score = max(0, min(100, int(b.get("score") or 0)))
        E.add_xp(con, uid, KEY, 0, best=score)
        return {"ok": True, "best": max(score, E.module_user(con, uid, KEY)["best"])}

    if action == "stats":
        u = ctx.target_user()
        tid = u["id"]
        total, pct = E.totals(con, tid, KEY)
        per = {r["cat2"]: {"n": r["n"], "pct": round(50 * r["s"] / r["n"])} for r in con.execute(
            "SELECT cat2, COUNT(*) n, SUM(result) s FROM answers WHERE user_id=? AND module=? GROUP BY cat2", (tid, KEY))}
        regions = [{"name": rn, "countries": [{"num": n, "name": COUNTRIES[n][0], **per.get(COUNTRIES[n][0], {"n": 0, "pct": None})}
                                              for n in ns]} for rn, ns in REGIONS.values()]
        mu = E.module_user(con, tid, KEY)
        return {"user": {"id": tid, "name": u["name"]}, "total": total, "pct": pct, "xp": mu["xp"], "best": mu["best"],
                "streak": E.streak(con, tid, KEY), "days": E.last14(con, tid, KEY), "regions": regions,
                "mistakes": E.recent_mistakes(con, tid, KEY)}

    raise ApiError(404, "Unknown")
