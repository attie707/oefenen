"""Ukrainian for beginners: alphabet, words, phrases, listening. Menus follow the user's language (en/nl)."""
import re

import engine as E
from engine import ApiError
from . import content as C
from . import lessons as L

KEY = "oekraiens"
ICON = "🇺🇦"
TITLE = {"en": "Ukrainian", "nl": "Oekraïens"}
DESC = {"en": "Cyrillic alphabet, words and phrases for talking with the family",
        "nl": "Het Cyrillische alfabet, woorden en zinnetjes om met de familie te praten"}
TTS_LANG, TTS_AZURE, TTS_PIPER = "uk-UA", "uk-UA-PolinaNeural", "uk_UA-ukrainian_tts-medium"
# The family learns Ukrainian through English. Set to None to follow each user's language setting (en/nl) instead.
FIXED_LANG = "en"
MODE_NAMES = {k: v["en"][0] for k, v in C.EXERCISES.items()}
GET_ACTIONS = ("lessons", "lesson")


def phrases():
    return C.all_phrases() | L.phrases()


def lesson_status(con, uid):
    rows = con.execute("SELECT key, box FROM progress WHERE user_id=? AND module=? AND key LIKE 'les:%'", (uid, KEY)).fetchall()
    return {r["key"][4:]: r["box"] for r in rows}


def weak_set(con, uid):
    return {k.split(":", 1)[1] for k in E.weak_keys(con, uid, KEY) if not k.startswith("les:")}


def check(given, q):
    if q["kind"] == "build":
        g = " ".join(re.sub(r"[.,!?]", " ", (given or "").lower()).split())
        return 2 if g in [a.lower() for a in q["accepted"]] else 0
    return E.check_text(given, q["accepted"])


def handle(action, ctx):
    con, me = ctx.con, ctx.me
    uid, lang = me["id"], FIXED_LANG or me["lang"]

    if action == "home":
        mu = E.module_user(con, uid, KEY)
        groups = [{"key": g["key"], "icon": g["icon"], "title": g["title"][lang], "desc": g["desc"][lang],
                   "ex": [{"key": e, "name": C.EXERCISES[e][lang][0], "desc": C.EXERCISES[e][lang][1]} for e in g["ex"]],
                   "focus": [{"key": k, "name": n[lang]} for k, n in g["focus"]]} for g in C.GROUPS]
        return {"name": me["name"], "lang": lang, "xp": mu["xp"], "streak": E.streak(con, uid, KEY),
                "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL, "groups": groups,
                "weak_count": len(weak_set(con, uid)),
                "lessons_done": sum(1 for b in lesson_status(con, uid).values() if b >= 5), "lessons_total": len(L.LESSONS)}

    if action == "lessons":
        st = lesson_status(con, uid)
        return [{"id": l["id"], "title": l["title"], "short": l["short"], "done": st.get(l["id"], 0) >= 5,
                 "tried": l["id"] in st} for l in L.LESSONS]

    if action == "lesson":
        lid = ctx.qs.get("id", [""])[0]
        if lid not in L.LESSON_BY_ID:
            raise ApiError(404, "Lesson not found")
        ids = [l["id"] for l in L.LESSONS]
        i = ids.index(lid)
        return {**L.public(L.LESSON_BY_ID[lid]), "next": ids[i + 1] if i + 1 < len(ids) else None}

    if action == "lesson/done":
        b = ctx.body()
        lid = b.get("id")
        if lid not in L.LESSON_BY_ID:
            raise ApiError(404, "Lesson not found")
        total = max(1, int(b.get("total") or 1))
        score = max(0, min(total, int(b.get("score") or 0)))
        passed = score / total >= 0.6
        con.execute("""INSERT INTO progress(user_id,module,key,box,seen,wrong,last_ts) VALUES(?,?,?,?,1,?,strftime('%s','now'))
                       ON CONFLICT(user_id,module,key) DO UPDATE SET box=MAX(box, excluded.box), seen=seen+1,
                       wrong=wrong+excluded.wrong, last_ts=excluded.last_ts""",
                    (uid, KEY, "les:" + lid, 5 if passed else 1, total - score))
        E.add_xp(con, uid, KEY, 5 * score)
        return {"passed": passed, "xp_gained": 5 * score}

    if action == "alphabet":
        return {"letters": C.alphabet(lang), "groups": {g: n[lang] for g, (n, _) in C.LETTER_GROUPS.items()}}

    if action == "question":
        b = ctx.body()
        ex, focus = b.get("ex"), b.get("focus") or "alle"
        if ex not in C.EXERCISES:
            raise ApiError(400, "Unknown exercise")
        pool, note = C.pool(ex, focus, weak_set(con, uid))
        if not pool:
            raise ApiError(400, "Nothing to practise here yet")
        item = E.pick_item(con, uid, KEY, ex, pool)
        q = C.question(ex, item, lang)
        qid = E.store_question(q, uid, KEY)
        p = dict(q["prompt"])
        for k in ("word", "phrase"):
            if k in p:
                p[k + "_tr"] = C.translit(p[k])
        return {"qid": qid, "ex": ex, "kind": q["kind"], "prompt": p, "options": q.get("options"),
                "opt_style": q.get("opt_style", "text"), "opt_translit": q.get("opt_translit"), "tiles": q.get("tiles"),
                "tiles_tr": [C.translit(t) for t in q["tiles"]] if q.get("tiles") else None,
                "keyboard": q.get("keyboard", False), "note": note}

    if action == "answer":
        b = ctx.body()
        q = E.take_question(b.get("qid"), uid, KEY)
        given = (b.get("answer") or "")[:200]
        result = check(given, q)
        E.update_box(con, uid, KEY, f"{q['ex']}:{q['item']}", result)
        grp, cat = C.category(q["item"])
        E.record_answer(con, uid, KEY, q["ex"], None, q["item"], grp, cat,
                        f'{C.EXERCISES[q["ex"]]["en"][0]}: {C.item_label(q["item"], "en")[0]}', given, q["answer"], result)
        xp = {2: E.XP_CORRECT, 1: E.XP_ALMOST, 0: 0}[result]
        E.add_xp(con, uid, KEY, xp)
        return {"result": ["wrong", "almost", "correct"][result], "answer": q["answer"], "accepted": q["accepted"],
                "say": q["say"], "info": q.get("info"), "kind": q["kind"], "xp_gained": xp,
                "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL}

    if action == "stats":
        u = ctx.target_user()
        tid = u["id"]
        total, pct = E.totals(con, tid, KEY)
        cats = [{"grp": C.GROUP_NAMES.get(r["cat1"], {}).get(lang, r["cat1"]), "cat": C.CAT_NAMES.get(r["cat2"], {}).get(lang, r["cat2"]),
                 "n": r["n"], "pct": round(50 * r["s"] / r["n"])} for r in con.execute(
            "SELECT cat1, cat2, COUNT(*) n, SUM(result) s FROM answers WHERE user_id=? AND module=? "
            "GROUP BY cat1, cat2 ORDER BY cat1, cat2", (tid, KEY))]
        weak = []
        for r in con.execute("SELECT key, box, seen, wrong FROM progress WHERE user_id=? AND module=? AND wrong>0 "
                             "ORDER BY box ASC, wrong DESC LIMIT 20", (tid, KEY)):
            ex, item = r["key"].split(":", 1)
            if ex in C.EXERCISES:
                try:
                    label, say = C.item_label(item, lang)
                except KeyError:
                    continue
                weak.append({"label": label, "say": say, "ex": C.EXERCISES[ex][lang][0],
                             "wrong": r["wrong"], "seen": r["seen"], "box": r["box"]})
        return {"user": {"id": tid, "name": u["name"]}, "total": total, "pct": pct,
                "xp": E.module_user(con, tid, KEY)["xp"], "streak": E.streak(con, tid, KEY),
                "days": E.last14(con, tid, KEY), "cats": cats, "weak": weak,
                "mistakes": E.recent_mistakes(con, tid, KEY)}

    raise ApiError(404, "Unknown")
