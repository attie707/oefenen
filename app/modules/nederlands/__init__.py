"""Dutch for beginners (A1-A2), all in Dutch: words, verbs, sentences, listening."""
import re

import engine as E
from engine import ApiError
from . import content as C
from . import lessons as L

KEY = "nederlands"
ICON = "🇳🇱"
TITLE = {"en": "Dutch", "nl": "Nederlands"}
DESC = {"en": "Words, verbs, sentences and listening (A1–A2)",
        "nl": "Woorden, werkwoorden, zinnen en luisteren (A1–A2)"}
TTS_LANG, TTS_AZURE, TTS_PIPER = "nl-NL", "nl-NL-FennaNeural", "nl_BE-nathalie-medium"
MODE_NAMES = {k: v["name"] for k, v in C.EXERCISES.items()}
GET_ACTIONS = ("lessons", "lesson")


def phrases():
    return C.all_phrases() | L.phrases()


def lesson_status(con, uid):
    rows = con.execute("SELECT key, box FROM progress WHERE user_id=? AND module=? AND key LIKE 'les:%'", (uid, KEY)).fetchall()
    return {r["key"][4:]: r["box"] for r in rows}


def weak_set(con, uid):
    return {k.split(":", 1)[1] for k in E.weak_keys(con, uid, KEY)}


def check(given, q):
    if q["kind"] == "build":
        g = " ".join(re.sub(r"[.,?!]", " ", (given or "").lower()).split())
        return 2 if g in [a.lower() for a in q["accepted"]] else 0
    return E.check_text(given, q["accepted"])


def handle(action, ctx):
    con, me = ctx.con, ctx.me
    uid = me["id"]

    if action == "home":
        mu = E.module_user(con, uid, KEY)
        return {"name": me["name"], "role": me["role"], "xp": mu["xp"], "streak": E.streak(con, uid, KEY),
                "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL, "groups": C.GROUPS,
                "weak_count": len(weak_set(con, uid)),
                "lessons_done": sum(1 for b in lesson_status(con, uid).values() if b >= 5), "lessons_total": len(L.LESSONS)}

    if action == "lessons":
        st = lesson_status(con, uid)
        return [{"id": l["id"], "title": l["title"], "short": l["short"], "done": st.get(l["id"], 0) >= 5,
                 "tried": l["id"] in st} for l in L.LESSONS]

    if action == "lesson":
        lid = ctx.qs.get("id", [""])[0]
        if lid not in L.LESSON_BY_ID:
            raise ApiError(404, "Les niet gevonden")
        ids = [l["id"] for l in L.LESSONS]
        i = ids.index(lid)
        return {**L.public(L.LESSON_BY_ID[lid]), "next": ids[i + 1] if i + 1 < len(ids) else None}

    if action == "lesson/done":
        b = ctx.body()
        lid = b.get("id")
        if lid not in L.LESSON_BY_ID:
            raise ApiError(404, "Les niet gevonden")
        total = max(1, int(b.get("total") or 1))
        score = max(0, min(total, int(b.get("score") or 0)))
        passed = score / total >= 0.6
        con.execute("""INSERT INTO progress(user_id,module,key,box,seen,wrong,last_ts) VALUES(?,?,?,?,1,?,strftime('%s','now'))
                       ON CONFLICT(user_id,module,key) DO UPDATE SET box=MAX(box, excluded.box), seen=seen+1,
                       wrong=wrong+excluded.wrong, last_ts=excluded.last_ts""",
                    (uid, KEY, "les:" + lid, 5 if passed else 1, total - score))
        E.add_xp(con, uid, KEY, 5 * score)
        return {"passed": passed, "xp_gained": 5 * score}

    if action == "question":
        b = ctx.body()
        ex, focus = b.get("ex"), b.get("focus") or "alle"
        if ex not in C.EXERCISES:
            raise ApiError(400, "Onbekende oefening")
        pool, note = C.pool(ex, focus, weak_set(con, uid))
        if not pool:
            raise ApiError(400, "Hier zijn (nog) geen oefeningen")
        item = E.pick_item(con, uid, KEY, ex, pool)
        q = C.question(ex, item)
        qid = E.store_question(q, uid, KEY)
        return {"qid": qid, "ex": ex, "kind": q["kind"], "prompt": q["prompt"], "options": q.get("options"),
                "opt_style": q.get("opt_style", "text"), "tiles": q.get("tiles"), "note": note}

    if action == "answer":
        b = ctx.body()
        q = E.take_question(b.get("qid"), uid, KEY, "Vraag verlopen, we gaan door met een nieuwe")
        given = (b.get("answer") or "")[:200]
        result = check(given, q)
        E.update_box(con, uid, KEY, f"{q['ex']}:{q['item']}", result)
        grp, cat = C.category(q["item"])
        prompt = f'{C.EXERCISES[q["ex"]]["name"]}: {C.item_label(q["item"])[0]}'
        E.record_answer(con, uid, KEY, q["ex"], None, q["item"], grp, cat, prompt, given, q["answer"], result)
        xp = {2: E.XP_CORRECT, 1: E.XP_ALMOST, 0: 0}[result]
        E.add_xp(con, uid, KEY, xp)
        lesson = None
        if q["item"] in C.SENTS:
            lid = L.LESSON_FOR_CAT.get(C.SENTS[q["item"]]["cat"])
            if lid:
                lesson = {"id": lid, "title": L.LESSON_BY_ID[lid]["title"]}
        return {"result": ["wrong", "almost", "correct"][result], "answer": q["answer"], "accepted": q["accepted"],
                "say": q["say"], "info": q.get("info"), "kind": q["kind"], "lesson": lesson,
                "xp_gained": xp, "xp": E.module_user(con, uid, KEY)["xp"],
                "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL}

    if action == "stats":
        u = ctx.target_user()
        tid = u["id"]
        total, pct = E.totals(con, tid, KEY)
        cats = [{"grp": r["cat1"], "cat": r["cat2"], "n": r["n"], "pct": round(50 * r["s"] / r["n"])} for r in con.execute(
            "SELECT cat1, cat2, COUNT(*) n, SUM(result) s FROM answers WHERE user_id=? AND module=? "
            "GROUP BY cat1, cat2 ORDER BY cat1, cat2", (tid, KEY))]
        weak = []
        for r in con.execute("SELECT key, box, seen, wrong FROM progress WHERE user_id=? AND module=? AND wrong>0 "
                             "ORDER BY box ASC, wrong DESC LIMIT 20", (tid, KEY)):
            ex, item = r["key"].split(":", 1)
            if ex in C.EXERCISES:
                label, say = C.item_label(item)
                weak.append({"label": label, "say": say, "ex": C.EXERCISES[ex]["name"],
                             "wrong": r["wrong"], "seen": r["seen"], "box": r["box"]})
        return {"user": {"id": tid, "name": u["name"]}, "total": total, "pct": pct,
                "xp": E.module_user(con, tid, KEY)["xp"], "streak": E.streak(con, tid, KEY),
                "days": E.last14(con, tid, KEY), "cats": cats, "weak": weak,
                "mistakes": E.recent_mistakes(con, tid, KEY)}

    raise ApiError(404, "Unknown")
