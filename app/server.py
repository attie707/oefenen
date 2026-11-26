"""Oefenen: one learning platform, one login, several subjects (modules).

Start:  python server.py   (port 8080, database in ./data/oefenen.db)
Environment: PORT, DATA_DIR (the login cookie is marked Secure automatically when the visitor uses https via a proxy),
             LEGACY_DBS="frans=/path/frans.db,nederlands=/path/nederlands.db" (one-time import)
"""
import csv
import hashlib
import io
import json
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import engine as E
import sso
from engine import ApiError
from modules import MODULES
from tts import TTS

PORT = int(os.environ.get("PORT", "8080"))
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(HERE, "data"))
DB_PATH = os.path.join(DATA_DIR, "oefenen.db")
STATIC = os.path.join(HERE, "static")
SESSION_DAYS = 30
LANGS = ("en", "nl")
ROLES = {"student": {"en": "Student", "nl": "Leerling"},
         "teacher": {"en": "Teacher / parent", "nl": "Docent / ouder"},
         "admin": {"en": "Administrator", "nl": "Beheerder"}}
RANK = {"student": 0, "teacher": 1, "admin": 2}
STAFF = ("teacher", "admin")
PW_MIN = 10
FAILS = defaultdict(list)

os.makedirs(DATA_DIR, exist_ok=True)
SPEECH = {k: TTS(os.path.join(DATA_DIR, k), m.TTS_LANG, m.TTS_AZURE, m.phrases(), piper_voice=m.TTS_PIPER)
          for k, m in MODULES.items()}

MSG = {
    "not_logged_in": {"en": "Not logged in", "nl": "Niet ingelogd"},
    "must_change": {"en": "Choose a new password first", "nl": "Kies eerst een nieuw wachtwoord"},
    "admin_only": {"en": "Only for the administrator", "nl": "Alleen voor de beheerder"},
    "staff_only": {"en": "Only for teachers and parents", "nl": "Alleen voor docenten en ouders"},
}


# ---------------- database ----------------
def db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with db() as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student', pw_hash TEXT NOT NULL, salt TEXT NOT NULL,
            created INTEGER NOT NULL, must_change INTEGER NOT NULL DEFAULT 1, lang TEXT NOT NULL DEFAULT 'en');
        CREATE TABLE IF NOT EXISTS sessions(
            token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS module_users(
            user_id INTEGER NOT NULL, module TEXT NOT NULL, xp INTEGER NOT NULL DEFAULT 0,
            best INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(user_id, module));
        CREATE TABLE IF NOT EXISTS progress(
            user_id INTEGER NOT NULL, module TEXT NOT NULL, key TEXT NOT NULL, box INTEGER NOT NULL DEFAULT 0,
            seen INTEGER NOT NULL DEFAULT 0, wrong INTEGER NOT NULL DEFAULT 0, last_ts INTEGER,
            PRIMARY KEY(user_id, module, key));
        CREATE TABLE IF NOT EXISTS answers(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, module TEXT NOT NULL, ts INTEGER NOT NULL,
            day TEXT NOT NULL, mode TEXT NOT NULL, level INTEGER, item TEXT NOT NULL, cat1 TEXT, cat2 TEXT,
            prompt TEXT, given TEXT, expected TEXT, result INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS ix_answers_user ON answers(user_id, module, id);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
        """)
        ucols = {r[1] for r in con.execute("PRAGMA table_info(users)")}
        if "email" not in ucols:
            con.execute("ALTER TABLE users ADD COLUMN email TEXT")
        scols = {r[1] for r in con.execute("PRAGMA table_info(sessions)")}
        if "via" not in scols:
            con.execute("ALTER TABLE sessions ADD COLUMN via TEXT NOT NULL DEFAULT 'password'")
        migrate_legacy(con)


def migrate_legacy(con):
    """One-time import of the old separate apps (frans-oefenen, nederlands-oefenen)."""
    spec = os.environ.get("LEGACY_DBS", "")
    if not spec or con.execute("SELECT 1 FROM meta WHERE key='migrated'").fetchone():
        return
    if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return
    for part in spec.split(","):
        if "=" not in part:
            continue
        module, path = part.split("=", 1)
        if module not in MODULES or not os.path.exists(path):
            continue
        old = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        old.row_factory = sqlite3.Row
        ucols = {r[1] for r in old.execute("PRAGMA table_info(users)")}
        idmap = {}
        for u in old.execute("SELECT * FROM users"):
            mc = u["must_change"] if "must_change" in ucols else 1
            role = u["role"] if u["role"] in ROLES else "student"
            ex = con.execute("SELECT * FROM users WHERE username=?", (u["username"],)).fetchone()
            if ex:
                idmap[u["id"]] = ex["id"]
                if RANK[role] > RANK[ex["role"]]:
                    con.execute("UPDATE users SET role=? WHERE id=?", (role, ex["id"]))
                if ex["must_change"] and not mc:       # keep the password the user already made strong
                    con.execute("UPDATE users SET pw_hash=?, salt=?, must_change=0 WHERE id=?",
                                (u["pw_hash"], u["salt"], ex["id"]))
            else:
                cur = con.execute("INSERT INTO users(username,name,role,pw_hash,salt,created,must_change) "
                                  "VALUES(?,?,?,?,?,?,?)", (u["username"], u["name"], role, u["pw_hash"],
                                                            u["salt"], u["created"], mc))
                idmap[u["id"]] = cur.lastrowid
            con.execute("INSERT OR REPLACE INTO module_users(user_id,module,xp,best) VALUES(?,?,?,?)",
                        (idmap[u["id"]], module, u["xp"], u["speed_best"] if "speed_best" in ucols else 0))
        for r in old.execute("SELECT * FROM progress"):
            if r["user_id"] in idmap:
                con.execute("INSERT OR REPLACE INTO progress VALUES(?,?,?,?,?,?,?)",
                            (idmap[r["user_id"]], module, r["key"], r["box"], r["seen"], r["wrong"], r["last_ts"]))
        n = 0
        for r in old.execute("SELECT * FROM answers ORDER BY id"):
            if r["user_id"] in idmap:
                con.execute("INSERT INTO answers(user_id,module,ts,day,mode,level,item,cat1,cat2,prompt,given,expected,result) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (idmap[r["user_id"]], module, r["ts"], r["day"], r["mode"], r["level"], r["item"],
                             r["verb"], r["pron"], r["prompt"], r["given"], r["expected"], r["result"]))
                n += 1
        old.close()
        print(f"Imported {len(idmap)} accounts and {n} answers from {module} ({path})", flush=True)
    con.execute("INSERT OR REPLACE INTO meta VALUES('migrated', ?)", (str(int(time.time())),))


def hash_pw(pw, salt=None):
    salt = salt or secrets.token_hex(16)
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex(), salt


PW_TEXT = {
    "len": {"en": f"at least {PW_MIN} characters", "nl": f"minstens {PW_MIN} tekens"},
    "lower": {"en": "a lowercase letter", "nl": "een kleine letter"},
    "upper": {"en": "a capital letter", "nl": "een hoofdletter"},
    "digit": {"en": "a digit", "nl": "een cijfer"},
    "special": {"en": "a special character (like ! ? # @)", "nl": "een speciaal teken (zoals ! ? # @)"},
    "missing": {"en": "Password needs: ", "nl": "Wachtwoord mist: "},
    "username": {"en": "The password may not contain your username", "nl": "Het wachtwoord mag je gebruikersnaam niet bevatten"},
}


def password_problem(pw, username="", lang="en"):
    checks = [("len", len(pw) >= PW_MIN), ("lower", re.search(r"[a-z]", pw)), ("upper", re.search(r"[A-Z]", pw)),
              ("digit", re.search(r"[0-9]", pw)), ("special", re.search(r"[^A-Za-z0-9]", pw))]
    missing = [PW_TEXT[k][lang] for k, ok in checks if not ok]
    if missing:
        return PW_TEXT["missing"][lang] + ", ".join(missing)
    if username and username.lower() in pw.lower():
        return PW_TEXT["username"][lang]
    return None


class Ctx:
    """What a module gets to work with."""
    def __init__(self, handler, con, me, qs):
        self.h, self.con, self.me, self.qs = handler, con, me, qs
        self._body = None

    def body(self):
        if self._body is None:
            self._body = self.h.body()
        return self._body

    def target_user(self):
        return self.h.target_user(self.con, self.me, self.qs)


MIME = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml", ".png": "image/png",
        ".json": "application/json", ".ico": "image/x-icon"}


class Handler(BaseHTTPRequestHandler):
    server_version = "Oefenen/2.0"

    def log_message(self, fmt, *args):
        if os.environ.get("QUIET") != "1":
            super().log_message(fmt, *args)

    # ---- helpers ----
    def send(self, status, body, ctype="application/json; charset=utf-8", headers=None):
        headers = dict(headers or {})
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", headers.pop("Cache-Control", "no-store"))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        if getattr(self, "_set_cookie", None) and "Set-Cookie" not in headers:
            headers["Set-Cookie"] = self._set_cookie
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 100_000:
            raise ApiError(413, "Too large")
        if not n:
            return {}
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            raise ApiError(415, "JSON expected")
        try:
            return json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            raise ApiError(400, "Invalid JSON")

    def token(self):
        if getattr(self, "_sso_token", None):
            return self._sso_token
        c = SimpleCookie(self.headers.get("Cookie") or "")
        return c["sid"].value if "sid" in c else None

    def sso_login(self, con):
        """Log in automatically when Cloudflare Access vouches for an e-mail address that belongs to an account."""
        self.sso_email = None
        if not sso.ENABLED:
            return
        tok = self.token()
        if tok and con.execute("SELECT 1 FROM sessions WHERE token=? AND created>?",
                               (tok, time.time() - SESSION_DAYS * 86400)).fetchone():
            return
        c = SimpleCookie(self.headers.get("Cookie") or "")
        jwt = self.headers.get("Cf-Access-Jwt-Assertion") or (c["CF_Authorization"].value if "CF_Authorization" in c else "")
        email = sso.email_from(jwt)
        if not email:
            return
        self.sso_email = email
        u = con.execute("SELECT id, must_change FROM users WHERE lower(email)=?", (email,)).fetchone()
        if u:
            if u["must_change"]:
                # first Google login: retire the temporary password, the account is now 'Google only'
                h, salt = hash_pw(secrets.token_urlsafe(24))
                con.execute("UPDATE users SET pw_hash=?, salt=?, must_change=0 WHERE id=?", (h, salt, u["id"]))
            new = secrets.token_urlsafe(32)
            con.execute("INSERT INTO sessions(token,user_id,created,via) VALUES(?,?,?,'sso')", (new, u["id"], int(time.time())))
            con.commit()
            self._sso_token = new
            self._set_cookie = self.cookie(new, SESSION_DAYS * 86400)

    def user(self, con, required=True, admin=False, staff=False, pending_ok=False):
        tok, u = self.token(), None
        if tok:
            u = con.execute("SELECT u.*, s.via AS via FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.created>?",
                            (tok, time.time() - SESSION_DAYS * 86400)).fetchone()
        if required and not u:
            raise ApiError(401, MSG["not_logged_in"]["en"])
        lang = u["lang"] if u else "en"
        if u and u["must_change"] and u["via"] != "sso" and not pending_ok:
            raise ApiError(403, "must_change")
        if admin and u["role"] != "admin":
            raise ApiError(403, MSG["admin_only"][lang])
        if staff and u["role"] not in STAFF:
            raise ApiError(403, MSG["staff_only"][lang])
        return u

    def target_user(self, con, me, qs):
        uid = qs.get("user", [None])[0]
        if uid and me["role"] in STAFF:
            u = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
            if not u:
                raise ApiError(404, "User not found")
            if me["role"] == "teacher" and u["role"] != "student" and u["id"] != me["id"]:
                raise ApiError(403, MSG["staff_only"][me["lang"]])
            return u
        return me

    def via_https(self):
        """True when the visitor uses https through a proxy (Nginx Proxy Manager, Cloudflare)."""
        proto = (self.headers.get("X-Forwarded-Proto") or "").lower()
        return proto == "https" or '"https"' in (self.headers.get("CF-Visitor") or "")

    def cookie(self, value, max_age):
        # Secure only when the browser really talks https; otherwise the browser would silently drop the
        # cookie on a plain http address (e.g. http://192.168.1.130:8080) and login would seem to do nothing.
        secure = self.via_https()
        return f"sid={value}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}" + ("; Secure" if secure else "")

    # ---- routing ----
    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def route(self, method):
        url = urlparse(self.path)
        path, qs = url.path, parse_qs(url.query)
        self._sso_token = self._set_cookie = self.sso_email = None
        try:
            if not path.startswith("/api/"):
                if method != "GET":
                    raise ApiError(405, "Not allowed")
                return self.static(path)
            con = db()
            try:
                with con:
                    self.sso_login(con)
                    if path.startswith("/api/m/"):
                        res = self.module_call(con, path[7:], method, qs)
                    else:
                        fn = getattr(self, f"api_{method.lower()}_{path[5:].replace('/', '_').replace('.', '_')}", None)
                        if not fn:
                            raise ApiError(404, "Unknown")
                        res = fn(con, qs)
            finally:
                con.close()
            if res is not None:
                self.send(200, res)
        except ApiError as e:
            self.send(e.status, {"error": e.msg})
        except Exception:  # noqa
            import traceback
            traceback.print_exc()
            self.send(500, {"error": "Something went wrong on the server"})

    def module_call(self, con, rest, method, qs):
        key, _, action = rest.partition("/")
        mod = MODULES.get(key)
        if not mod:
            raise ApiError(404, "Unknown subject")
        me = self.user(con)
        if action == "tts" and method == "GET":
            res = SPEECH[key].get(qs.get("t", [""])[0])
            if not res:
                raise ApiError(404, "No sound")
            self.send(200, res[0], res[1], {"Cache-Control": "private, max-age=604800"})
            return None
        if method == "GET" and action not in ("home", "stats", "alphabet") + tuple(getattr(mod, "GET_ACTIONS", ())):
            raise ApiError(405, "Not allowed")
        return mod.handle(action, Ctx(self, con, me, qs))

    def static(self, path):
        if path.strip("/") in MODULES and not path.endswith("/"):
            self.send(301, b"", "text/plain", {"Location": path + "/"})
            return
        if path in ("/", ""):
            path = "/index.html"
        first = path.strip("/").split("/")[0]
        full = os.path.normpath(os.path.join(STATIC, path.lstrip("/")))
        if path.endswith("/"):
            full = os.path.join(full, "index.html")
        if not full.startswith(STATIC + os.sep) or not os.path.isfile(full):
            full = os.path.join(STATIC, first, "index.html") if first in MODULES else os.path.join(STATIC, "index.html")
        with open(full, "rb") as f:
            data = f.read()
        self.send(200, data, MIME.get(os.path.splitext(full)[1], "application/octet-stream"))

    # ---------------- account ----------------
    def me_json(self, u):
        return {"id": u["id"], "name": u["name"], "username": u["username"], "role": u["role"],
                "role_name": ROLES[u["role"]][u["lang"]], "lang": u["lang"], "email": u["email"],
                "must_change": bool(u["must_change"]) and u["via"] != "sso", "sso": u["via"] == "sso"}

    def api_get_state(self, con, qs):
        setup = con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        u = None if setup else self.user(con, required=False, pending_ok=True)
        return {"setup_needed": setup, "pw_min": PW_MIN, "user": self.me_json(u) if u else None,
                "sso": {"enabled": sso.ENABLED, "unlinked_email": None if u else getattr(self, "sso_email", None)},
                "modules": [{"key": k, "icon": m.ICON, "title": m.TITLE, "desc": m.DESC, "tts": SPEECH[k].engine}
                            for k, m in MODULES.items()]}

    def api_post_setup(self, con, qs):
        if con.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            raise ApiError(400, "There is already an administrator")
        return self._create_user(con, self.body(), role="admin", login=True, must_change=0)

    def _create_user(self, con, b, role, login=False, must_change=1, lang="en"):
        username = (b.get("username") or "").strip().lower()
        name = (b.get("name") or "").strip() or username
        pw = b.get("password") or ""
        if not re.fullmatch(r"[a-z0-9._-]{2,30}", username):
            raise ApiError(400, {"en": "Username: 2–30 characters, only letters, digits, . _ -",
                                 "nl": "Gebruikersnaam: 2-30 tekens, alleen letters, cijfers, . _ -"}[lang])
        problem = password_problem(pw, username, lang)
        if problem:
            raise ApiError(400, problem)
        if con.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            raise ApiError(400, {"en": "That username already exists", "nl": "Die gebruikersnaam bestaat al"}[lang])
        user_lang = b.get("lang") if b.get("lang") in LANGS else "en"
        h, salt = hash_pw(pw)
        email = self._clean_email(con, b.get("email"), lang)
        cur = con.execute("INSERT INTO users(username,name,role,pw_hash,salt,created,must_change,lang,email) VALUES(?,?,?,?,?,?,?,?,?)",
                          (username, name[:40], role, h, salt, int(time.time()), must_change, user_lang, email))
        if login:
            return self._login(con, cur.lastrowid)
        return {"ok": True, "id": cur.lastrowid}

    def _clean_email(self, con, email, lang, uid=None):
        email = (email or "").strip().lower()
        if not email:
            return None
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ApiError(400, {"en": "That is not a valid e-mail address", "nl": "Dat is geen geldig e-mailadres"}[lang])
        if con.execute("SELECT 1 FROM users WHERE lower(email)=? AND id<>?", (email, uid or 0)).fetchone():
            raise ApiError(400, {"en": "That e-mail address is already linked to another account",
                                 "nl": "Dat e-mailadres hoort al bij een ander account"}[lang])
        return email

    def api_post_users_email(self, con, qs):
        me = self.user(con, admin=True)
        b = self.body()
        email = self._clean_email(con, b.get("email"), me["lang"], b.get("id"))
        con.execute("UPDATE users SET email=? WHERE id=?", (email, b.get("id")))
        con.execute("DELETE FROM sessions WHERE user_id=? AND via='sso'", (b.get("id"),))
        return {"ok": True}

    def _login(self, con, uid):
        tok = secrets.token_urlsafe(32)
        con.execute("INSERT INTO sessions(token,user_id,created,via) VALUES(?,?,?,'password')", (tok, uid, int(time.time())))
        con.execute("DELETE FROM sessions WHERE created<?", (time.time() - SESSION_DAYS * 86400,))
        con.commit()
        self.send(200, {"ok": True}, headers={"Set-Cookie": self.cookie(tok, SESSION_DAYS * 86400)})

    def api_post_login(self, con, qs):
        ip = self.headers.get("CF-Connecting-IP") or self.client_address[0]
        now = time.time()
        with E.LOCK:
            FAILS[ip] = [t for t in FAILS[ip] if now - t < 600]
            if len(FAILS[ip]) >= 10:
                raise ApiError(429, "Too many attempts. Try again in 10 minutes.")
        b = self.body()
        u = con.execute("SELECT * FROM users WHERE username=?", ((b.get("username") or "").strip().lower(),)).fetchone()
        if not u or not secrets.compare_digest(hash_pw(b.get("password") or "", u["salt"])[0], u["pw_hash"]):
            with E.LOCK:
                FAILS[ip].append(now)
            raise ApiError(401, "Username or password is incorrect")
        return self._login(con, u["id"])

    def api_post_logout(self, con, qs):
        tok = self.token()
        via = None
        if tok:
            r = con.execute("SELECT via FROM sessions WHERE token=?", (tok,)).fetchone()
            via = r["via"] if r else None
            con.execute("DELETE FROM sessions WHERE token=?", (tok,))
        con.commit()
        # after a Google login, also end the Cloudflare Access session, otherwise you'd be logged in again at once
        self.send(200, {"ok": True, "sso_logout": "/cdn-cgi/access/logout" if via == "sso" else None},
                  headers={"Set-Cookie": self.cookie("", 0)})

    def api_post_password(self, con, qs):
        me = self.user(con, pending_ok=True)
        b = self.body()
        old, new = b.get("old") or "", b.get("new") or ""
        if not secrets.compare_digest(hash_pw(old, me["salt"])[0], me["pw_hash"]):
            raise ApiError(400, {"en": "Current password is incorrect", "nl": "Huidig wachtwoord klopt niet"}[me["lang"]])
        problem = password_problem(new, me["username"], me["lang"])
        if problem:
            raise ApiError(400, problem)
        if new == old:
            raise ApiError(400, {"en": "Choose a different password than the old one", "nl": "Kies een ander wachtwoord dan het oude"}[me["lang"]])
        h, salt = hash_pw(new)
        con.execute("UPDATE users SET pw_hash=?, salt=?, must_change=0 WHERE id=?", (h, salt, me["id"]))
        con.execute("DELETE FROM sessions WHERE user_id=? AND token<>?", (me["id"], self.token()))
        return {"ok": True}

    def api_post_settings(self, con, qs):
        me = self.user(con)
        b = self.body()
        if b.get("lang") in LANGS:
            con.execute("UPDATE users SET lang=? WHERE id=?", (b["lang"], me["id"]))
        name = (b.get("name") or "").strip()
        if name:
            con.execute("UPDATE users SET name=? WHERE id=?", (name[:40], me["id"]))
        return {"ok": True}

    # ---------------- landing page + overview ----------------
    def api_get_portal(self, con, qs):
        me = self.user(con)
        return {"streak": E.streak(con, me["id"]), "today": E.today_count(con, me["id"]), "goal": E.DAILY_GOAL,
                "modules": {k: E.summary(con, me["id"], k) for k in MODULES}}

    def api_get_users(self, con, qs):
        me = self.user(con, staff=True)
        out = []
        for u in con.execute("SELECT id, username, name, role, must_change, lang, email FROM users "
                             "ORDER BY CASE role WHEN 'student' THEN 0 WHEN 'teacher' THEN 1 ELSE 2 END, name"):
            if me["role"] != "admin" and u["role"] != "student":
                continue
            d = dict(u)
            d["role_name"] = ROLES[d["role"]][me["lang"]]
            d["modules"] = {k: E.summary(con, u["id"], k) for k in MODULES}
            d["last_ts"] = max([m["last_ts"] or 0 for m in d["modules"].values()] or [0]) or None
            d["today"] = sum(m["today"] for m in d["modules"].values())
            d["total"] = sum(m["total"] for m in d["modules"].values())
            out.append(d)
        return out

    def api_post_users_create(self, con, qs):
        me = self.user(con, admin=True)
        b = self.body()
        role = b.get("role") if b.get("role") in ROLES else "student"
        return self._create_user(con, b, role=role, lang=me["lang"])

    def api_post_users_role(self, con, qs):
        me = self.user(con, admin=True)
        b = self.body()
        if b.get("role") not in ROLES:
            raise ApiError(400, "Unknown role")
        if b.get("id") == me["id"] and b["role"] != "admin":
            raise ApiError(400, {"en": "You can't remove your own administrator role",
                                 "nl": "Je kunt je eigen beheerdersrol niet weghalen"}[me["lang"]])
        con.execute("UPDATE users SET role=? WHERE id=?", (b["role"], b.get("id")))
        return {"ok": True}

    def api_post_users_password(self, con, qs):
        me = self.user(con, admin=True)
        b = self.body()
        u = con.execute("SELECT username FROM users WHERE id=?", (b.get("id"),)).fetchone()
        if not u:
            raise ApiError(404, "User not found")
        problem = password_problem(b.get("password") or "", u["username"], me["lang"])
        if problem:
            raise ApiError(400, problem)
        h, salt = hash_pw(b["password"])
        con.execute("UPDATE users SET pw_hash=?, salt=?, must_change=1 WHERE id=?", (h, salt, b.get("id")))
        con.execute("DELETE FROM sessions WHERE user_id=?", (b.get("id"),))
        return {"ok": True}

    def api_post_users_delete(self, con, qs):
        me = self.user(con, admin=True)
        uid = self.body().get("id")
        if uid == me["id"]:
            raise ApiError(400, {"en": "You can't delete yourself", "nl": "Je kunt jezelf niet verwijderen"}[me["lang"]])
        for t in ("sessions", "progress", "answers", "module_users"):
            con.execute(f"DELETE FROM {t} WHERE user_id=?", (uid,))
        con.execute("DELETE FROM users WHERE id=?", (uid,))
        return {"ok": True}

    def api_get_export_csv(self, con, qs):
        me = self.user(con)
        module = qs.get("module", [""])[0]
        where, args = [], []
        if qs.get("user", [""])[0] == "all" and me["role"] in STAFF:
            where.append("u.role='student'")
            fname = "all-students"
        else:
            u = self.target_user(con, me, qs)
            where.append("a.user_id=?")
            args.append(u["id"])
            fname = u["username"]
        if module in MODULES:
            where.append("a.module=?")
            args.append(module)
            fname += "-" + module
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow(["name", "subject", "date", "time", "exercise", "level", "category", "question", "answer",
                    "correct answer", "result"])
        for r in con.execute(f"SELECT a.*, u.name FROM answers a JOIN users u ON u.id=a.user_id WHERE {' AND '.join(where)} "
                             "ORDER BY a.id", args):
            m = MODULES.get(r["module"])
            w.writerow([r["name"], m.TITLE["en"] if m else r["module"], r["day"], time.strftime("%H:%M", time.localtime(r["ts"])),
                        m.MODE_NAMES.get(r["mode"], r["mode"]) if m else r["mode"], r["level"] or "",
                        " / ".join(x for x in (r["cat1"], r["cat2"]) if x), r["prompt"], r["given"], r["expected"],
                        ["wrong", "almost (accent)", "correct"][r["result"]]])
        self.send(200, "﻿" + buf.getvalue(), "text/csv; charset=utf-8",
                  {"Content-Disposition": f'attachment; filename="oefenen-{fname}-{E.today()}.csv"'})


def main():
    init_db()
    print(f"Single sign-on: {'Cloudflare Access (' + sso.TEAM + ')' if sso.ENABLED else 'off'}", flush=True)
    for s in SPEECH.values():
        s.prewarm()
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Oefenen is running on http://0.0.0.0:{PORT}  (database: {DB_PATH})", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
