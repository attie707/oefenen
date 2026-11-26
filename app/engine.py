"""Shared learning engine for all modules: Leitner repetition, answer checking, scores."""
import datetime as dt
import random
import re
import secrets
import threading
import time
import unicodedata
from collections import defaultdict, deque

DAILY_GOAL = 20
XP_CORRECT, XP_ALMOST = 10, 4
BOX_WEIGHT = {0: 3, 1: 10, 2: 5, 3: 2, 4: 1, 5: 0.5}

LOCK = threading.Lock()
PENDING = {}                                      # qid -> question incl. answer
RECENT = defaultdict(lambda: deque(maxlen=4))     # (uid, module) -> last items


class ApiError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg)
        self.status, self.msg = status, msg


def today():
    return dt.date.today().isoformat()


# ---------------- pending questions ----------------
def store_question(q, uid, module):
    qid = secrets.token_urlsafe(12)
    q.update({"t": time.time(), "uid": uid, "module": module})
    with LOCK:
        for k in [k for k, v in PENDING.items() if time.time() - v["t"] > 3600]:
            PENDING.pop(k, None)
        PENDING[qid] = q
    return qid


def take_question(qid, uid, module, msg="Question expired, here is a new one"):
    with LOCK:
        q = PENDING.pop(qid, None)
    if not q or q["uid"] != uid or q["module"] != module:
        raise ApiError(400, msg)
    return q


# ---------------- Leitner ----------------
def load_progress(con, uid, module, mode):
    rows = con.execute("SELECT key, box, seen, wrong FROM progress WHERE user_id=? AND module=? AND key LIKE ?",
                       (uid, module, mode + ":%")).fetchall()
    return {r["key"].split(":", 1)[1]: dict(r) for r in rows}


def pick_item(con, uid, module, mode, pool):
    prog = load_progress(con, uid, module, mode)
    recent = RECENT[(uid, module)]
    cand = [i for i in pool if i not in recent] if len(pool) > 5 else list(pool)
    box1 = [i for i in cand if prog.get(i, {}).get("box") == 1]
    if box1 and random.random() < 0.35:
        choice = random.choice(box1)
    else:
        weights = [BOX_WEIGHT[prog.get(i, {}).get("box", 0)] for i in cand]
        choice = random.choices(cand, weights=weights)[0]
    recent.append(choice)
    return choice


def weak_keys(con, uid, module):
    """Set of 'mode:item' keys answered wrong that are not yet learned."""
    return {r["key"] for r in con.execute(
        "SELECT key FROM progress WHERE user_id=? AND module=? AND wrong>0 AND box<=2", (uid, module))}


def update_box(con, uid, module, key, result):
    p = con.execute("SELECT box FROM progress WHERE user_id=? AND module=? AND key=?", (uid, module, key)).fetchone()
    box = p["box"] if p else 0
    if result == 2:
        box = 2 if box == 0 else min(5, box + 1)
    elif result == 1:
        box = max(1, box)
    else:
        box = 1
    con.execute("""INSERT INTO progress(user_id,module,key,box,seen,wrong,last_ts) VALUES(?,?,?,?,1,?,?)
                   ON CONFLICT(user_id,module,key) DO UPDATE SET box=excluded.box, seen=seen+1,
                   wrong=wrong+excluded.wrong, last_ts=excluded.last_ts""",
                (uid, module, key, box, 1 if result < 2 else 0, int(time.time())))


def record_answer(con, uid, module, mode, level, item, cat1, cat2, prompt, given, expected, result):
    con.execute("INSERT INTO answers(user_id,module,ts,day,mode,level,item,cat1,cat2,prompt,given,expected,result) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (uid, module, int(time.time()), today(), mode, level, item, cat1, cat2, prompt, given, expected, result))


# ---------------- per-module totals ----------------
def module_user(con, uid, module):
    r = con.execute("SELECT xp, best FROM module_users WHERE user_id=? AND module=?", (uid, module)).fetchone()
    return {"xp": r["xp"], "best": r["best"]} if r else {"xp": 0, "best": 0}


def add_xp(con, uid, module, xp, best=None):
    con.execute("""INSERT INTO module_users(user_id,module,xp,best) VALUES(?,?,?,?)
                   ON CONFLICT(user_id,module) DO UPDATE SET xp=xp+excluded.xp, best=MAX(best, excluded.best)""",
                (uid, module, xp, best or 0))


def today_count(con, uid, module=None):
    if module:
        return con.execute("SELECT COUNT(*) FROM answers WHERE user_id=? AND module=? AND day=?", (uid, module, today())).fetchone()[0]
    return con.execute("SELECT COUNT(*) FROM answers WHERE user_id=? AND day=?", (uid, today())).fetchone()[0]


def streak(con, uid, module=None):
    if module:
        rows = con.execute("SELECT DISTINCT day FROM answers WHERE user_id=? AND module=?", (uid, module))
    else:
        rows = con.execute("SELECT DISTINCT day FROM answers WHERE user_id=?", (uid,))
    days = {r["day"] for r in rows}
    d = dt.date.today()
    if d.isoformat() not in days:
        d -= dt.timedelta(days=1)
    n = 0
    while d.isoformat() in days:
        n += 1
        d -= dt.timedelta(days=1)
    return n


def last14(con, uid, module):
    start = (dt.date.today() - dt.timedelta(days=13)).isoformat()
    per_day = {r["day"]: r for r in con.execute(
        "SELECT day, COUNT(*) n, SUM(result) s FROM answers WHERE user_id=? AND module=? AND day>=? GROUP BY day",
        (uid, module, start))}
    out = []
    for i in range(13, -1, -1):
        d = (dt.date.today() - dt.timedelta(days=i)).isoformat()
        r = per_day.get(d)
        out.append({"day": d, "n": r["n"] if r else 0, "pct": round(50 * r["s"] / r["n"]) if r else None})
    return out


def totals(con, uid, module):
    t = con.execute("SELECT COUNT(*) n, COALESCE(SUM(result),0) s FROM answers WHERE user_id=? AND module=?",
                    (uid, module)).fetchone()
    return t["n"], (round(50 * t["s"] / t["n"]) if t["n"] else None)


def summary(con, uid, module):
    """Compact progress line for the teacher overview and the landing page."""
    week = (dt.date.today() - dt.timedelta(days=6)).isoformat()
    r = con.execute("""SELECT COUNT(*) total, MAX(ts) last_ts,
                       SUM(CASE WHEN day=? THEN 1 ELSE 0 END) today,
                       SUM(CASE WHEN day>=? THEN 1 ELSE 0 END) week,
                       SUM(CASE WHEN day>=? THEN result ELSE 0 END) week_s
                       FROM answers WHERE user_id=? AND module=?""", (today(), week, week, uid, module)).fetchone()
    mu = module_user(con, uid, module)
    return {"total": r["total"] or 0, "last_ts": r["last_ts"], "today": r["today"] or 0, "week": r["week"] or 0,
            "week_pct": round(50 * r["week_s"] / r["week"]) if r["week"] else None,
            "streak": streak(con, uid, module), "xp": mu["xp"], "best": mu["best"]}


def recent_mistakes(con, uid, module, n=15):
    return [dict(r) for r in con.execute(
        "SELECT ts, prompt, given, expected, result FROM answers WHERE user_id=? AND module=? AND result<2 "
        "ORDER BY id DESC LIMIT ?", (uid, module, n))]


# ---------------- answer checking ----------------
def normalize(s):
    s = (s or "").strip().lower().rstrip(".!? ")
    s = re.sub(r"[’‘`´ʼ]", "'", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*'\s*", "'", s)
    return s.rstrip(".!? ")


def strip_accents(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def check_text(given, accepted):
    """2 = correct, 1 = only accents wrong, 0 = wrong."""
    g = normalize(given)
    ok = [normalize(a) for a in accepted]
    if g in ok:
        return 2
    if strip_accents(g) in [strip_accents(a) for a in ok]:
        return 1
    return 0
