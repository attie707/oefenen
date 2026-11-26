"""French for Dutch-speaking pupils: être, avoir and -er verbs."""
import random
import secrets
import time
from collections import defaultdict

import engine as E
from engine import ApiError
from . import content as C

KEY = "frans"
ICON = "🇫🇷"
TITLE = {"en": "French", "nl": "Frans"}
DESC = {"en": "être, avoir and -er verbs: quiz, spelling, listening",
        "nl": "être, avoir en -er werkwoorden: quiz, spelling, luisteren"}
TTS_LANG, TTS_AZURE, TTS_PIPER = "fr-FR", "fr-FR-DeniseNeural", "fr_FR-siwis-medium"
MODE_NAMES = {"mc": "Meerkeuze", "spell": "Spelling", "listen": "Luisteren", "dictee": "Dictee"}

SPEED_SECONDS = 60
XP_SPEED_BONUS, XP_LEVEL_UP = 5, 50
SPEED = {}


def phrases():
    return C.all_phrases()


def level_status(con, uid):
    out, unlocked = [], True
    for lv in C.LEVELS:
        rows = con.execute("SELECT result FROM answers WHERE user_id=? AND module=? AND mode='spell' AND level=? "
                           "ORDER BY id DESC LIMIT ?", (uid, KEY, lv["n"], C.LEVEL_UNLOCK_WINDOW)).fetchall()
        score = sum(r["result"] for r in rows) / (2 * len(rows)) if rows else 0
        passed = len(rows) >= C.LEVEL_UNLOCK_WINDOW and score >= C.LEVEL_UNLOCK_SCORE
        out.append({"n": lv["n"], "name": lv["name"], "desc": lv["desc"], "unlocked": unlocked,
                    "score": round(score * 100), "answered": len(rows), "passed": passed})
        unlocked = unlocked and passed
    return out


def weak_items(con, uid):
    items = {k.split(":", 1)[1] for k in E.weak_keys(con, uid, KEY)}
    return [i for i in items if i in C.ITEMS and not C.ITEMS[i]["neg"]]


def check(given, q):
    acc = list(q["accepted"])
    if q["fmt"] == "fill":
        acc.append(q["say"])
    return E.check_text(given, acc)


def handle(action, ctx):
    con, me = ctx.con, ctx.me
    uid = me["id"]

    if action == "home":
        mu = E.module_user(con, uid, KEY)
        return {"name": me["name"], "role": me["role"], "xp": mu["xp"], "streak": E.streak(con, uid, KEY),
                "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL, "speed_best": mu["best"],
                "levels": level_status(con, uid),
                "focus": [{"key": k, "name": v[0]} for k, v in C.MC_FOCUS.items()] +
                         [{"key": "weak", "name": "Mijn zwakke punten"}],
                "weak_count": len(weak_items(con, uid))}

    if action == "question":
        b = ctx.body()
        mode = b.get("mode")
        note, level, sid = None, None, b.get("speed")
        if mode == "mc":
            focus = b.get("focus", "all")
            if focus == "weak":
                pool = weak_items(con, uid)
                if len(pool) < 3:
                    pool, note = C.MC_FOCUS["all"][1], "Je hebt (nog) geen zwakke punten. Lekker bezig! We doen alles door elkaar."
            else:
                pool = C.MC_FOCUS.get(focus, C.MC_FOCUS["all"])[1]
            item = E.pick_item(con, uid, KEY, "mc", pool)
            q = C.make_question(item, random.choice(["fill", "translate"]), mc=True)
        elif mode == "spell":
            levels = level_status(con, uid)
            level = int(b.get("level") or 1)
            if not (1 <= level <= len(levels)) or not levels[level - 1]["unlocked"]:
                raise ApiError(400, "Dit niveau is nog op slot")
            lv = C.LEVELS[level - 1]
            item = E.pick_item(con, uid, KEY, "spell", lv["items"])
            q = C.make_question(item, lv["fmt"])
        elif mode in ("listen", "dictee"):
            focus = b.get("focus", "all")
            pool = weak_items(con, uid) if focus == "weak" else C.MC_FOCUS.get(focus, C.MC_FOCUS["all"])[1]
            if len(pool) < 3:
                pool, note = C.MC_FOCUS["all"][1], "Je hebt (nog) geen zwakke punten. We doen alles door elkaar."
            item = E.pick_item(con, uid, KEY, mode, pool)
            q = C.make_listen_question(item, "mc" if mode == "listen" else "dictee")
        else:
            raise ApiError(400, "Onbekende modus")
        q.update({"mode": mode, "level": level, "speed": sid})
        qid = E.store_question(q, uid, KEY)
        return {"qid": qid, "mode": mode, "fmt": q["fmt"], "prompt": q["prompt"],
                "options": q.get("options"), "level": level, "note": note}

    if action == "answer":
        b = ctx.body()
        q = E.take_question(b.get("qid"), uid, KEY, "Vraag verlopen, we gaan door met een nieuwe")
        given = (b.get("answer") or "")[:100]
        result = check(given, q)
        levels_before = level_status(con, uid) if q["mode"] == "spell" else None
        E.update_box(con, uid, KEY, f"{q['mode']}:{q['item']}", result)
        if q["fmt"] == "fill":
            prompt = f'{q["prompt"]["fr"]} ({q["prompt"]["inf"]})'
        elif "say" in q["prompt"]:
            prompt = "🔊 " + q["say"]
        else:
            prompt = q["prompt"]["nl"]
        E.record_answer(con, uid, KEY, q["mode"], q["level"], q["item"], q["verb"], C.base_pron(q["pron"]),
                        prompt, given, q["answer"], result)
        xp = {2: E.XP_CORRECT, 1: E.XP_ALMOST, 0: 0}[result]
        speed_score = None
        if q["speed"]:
            with E.LOCK:
                s = SPEED.get(q["speed"])
                if s and s["uid"] == uid and time.time() - s["t"] <= SPEED_SECONDS + 3 and result == 2:
                    s["score"] += 1
                    xp += XP_SPEED_BONUS
                speed_score = s["score"] if s else None
        unlocked = None
        if levels_before:
            for a, bf in zip(level_status(con, uid), levels_before):
                if a["unlocked"] and not bf["unlocked"]:
                    unlocked = a
                    xp += XP_LEVEL_UP
        E.add_xp(con, uid, KEY, xp)
        mu = E.module_user(con, uid, KEY)
        return {"result": ["wrong", "almost", "correct"][result], "answer": q["answer"],
                "accepted": q["accepted"], "say": q["say"], "fmt": q["fmt"],
                "nl": C.nl_phrase(q["verb"], q["pron"], C.ITEMS[q["item"]]["neg"]), "table": C.table(q["verb"], q["pron"]),
                "xp_gained": xp, "xp": mu["xp"], "today": E.today_count(con, uid, KEY), "goal": E.DAILY_GOAL,
                "unlocked": unlocked, "speed_score": speed_score}

    if action == "speed/start":
        sid = secrets.token_urlsafe(10)
        with E.LOCK:
            for k in [k for k, v in SPEED.items() if time.time() - v["t"] > 600]:
                SPEED.pop(k, None)
            SPEED[sid] = {"uid": uid, "t": time.time(), "score": 0}
        return {"sid": sid, "seconds": SPEED_SECONDS}

    if action == "speed/finish":
        with E.LOCK:
            s = SPEED.pop(ctx.body().get("sid"), None)
        if not s or s["uid"] != uid:
            raise ApiError(400, "Ronde niet gevonden")
        best = E.module_user(con, uid, KEY)["best"]
        E.add_xp(con, uid, KEY, 0, best=s["score"])
        return {"score": s["score"], "best": max(s["score"], best), "record": s["score"] > best}

    if action == "stats":
        u = ctx.target_user()
        tid = u["id"]
        total, pct = E.totals(con, tid, KEY)
        heat = defaultdict(dict)
        for r in con.execute("SELECT cat1, cat2, COUNT(*) n, SUM(result) s FROM answers WHERE user_id=? AND module=? "
                             "GROUP BY cat1, cat2", (tid, KEY)):
            heat[r["cat1"]][r["cat2"]] = {"n": r["n"], "pct": round(50 * r["s"] / r["n"])}
        verbs = sorted(heat, key=lambda v: (v not in ("être", "avoir"), v))
        weak = []
        for r in con.execute("SELECT key, box, seen, wrong FROM progress WHERE user_id=? AND module=? AND wrong>0 "
                             "ORDER BY box ASC, wrong DESC LIMIT 15", (tid, KEY)):
            item = C.ITEMS.get(r["key"].split(":", 1)[1])
            if item:
                weak.append({"fr": C.phrase(item["verb"], item["pron"], item["neg"]),
                             "nl": C.nl_phrase(item["verb"], item["pron"], item["neg"]),
                             "wrong": r["wrong"], "seen": r["seen"], "box": r["box"],
                             "mode": MODE_NAMES.get(r["key"].split(":", 1)[0], "")})
        mu = E.module_user(con, tid, KEY)
        return {"user": {"id": tid, "name": u["name"]}, "total": total, "pct": pct,
                "xp": mu["xp"], "streak": E.streak(con, tid, KEY), "speed_best": mu["best"],
                "days": E.last14(con, tid, KEY), "heat": {v: heat[v] for v in verbs},
                "prons": ["je", "tu", "il", "nous", "vous", "ils"],
                "weak": weak, "mistakes": E.recent_mistakes(con, tid, KEY), "levels": level_status(con, tid)}

    raise ApiError(404, "Unknown")
