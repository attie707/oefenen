"""Command-line admin tool, run inside the container as:  oefenen-admin <command>

  oefenen-admin list                 show all accounts
  oefenen-admin reset <username>     give the account a new temporary password (must be changed at login)
  oefenen-admin role <username> <student|teacher|admin>
  oefenen-admin email <username> <address>   link a Google address (use "-" to remove)
  oefenen-admin delete <username>            delete the account and all its scores
"""
import hashlib
import os
import secrets
import sqlite3
import sys

DB = os.path.join(os.environ.get("DATA_DIR", "/var/lib/oefenen"), "oefenen.db")
WORDS = ["Sun", "Cat", "Apple", "Cheese", "Moon", "Bike", "Beach", "Book", "Tree", "Train", "Cloud", "Star", "Boat", "Tulip", "Mango"]


def temp_password():
    a, b = secrets.SystemRandom().sample(WORDS, 2)
    return f"{a}-{b}{secrets.randbelow(90) + 10}{secrets.choice('!?#@')}"


def main(args):
    con = sqlite3.connect(DB, timeout=10)
    if not args or args[0] == "list":
        cols = {r[1] for r in con.execute("PRAGMA table_info(users)")}
        email = "email" if "email" in cols else "''"
        rows = con.execute(f"SELECT id, username, name, role, must_change, {email} FROM users ORDER BY id").fetchall()
        print("%-4s %-16s %-20s %-8s %-6s %s" % ("id", "username", "name", "role", "newpw", "google e-mail"))
        for r in rows:
            print("%-4s %-16s %-20s %-8s %-6s %s" % (r[0], r[1], r[2], r[3], "yes" if r[4] else "-", r[5] or "-"))
        return
    if args[0] == "reset" and len(args) == 2:
        user = args[1].strip().lower()
        if not con.execute("SELECT 1 FROM users WHERE username=?", (user,)).fetchone():
            sys.exit(f"No account '{user}'. Run 'oefenen-admin list' to see all usernames.")
        pw, salt = temp_password(), secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex()
        with con:
            con.execute("UPDATE users SET pw_hash=?, salt=?, must_change=1 WHERE username=?", (h, salt, user))
            con.execute("DELETE FROM sessions WHERE user_id=(SELECT id FROM users WHERE username=?)", (user,))
        print(f"Temporary password for {user}:  {pw}")
        print("Log in with it; you will then be asked to choose your own password.")
        return
    if args[0] == "role" and len(args) == 3 and args[2] in ("student", "teacher", "admin"):
        with con:
            n = con.execute("UPDATE users SET role=? WHERE username=?", (args[2], args[1].lower())).rowcount
        print("Done" if n else f"No account '{args[1]}'")
        return
    if args[0] == "email" and len(args) == 3:
        user, addr = args[1].lower(), args[2].strip().lower()
        addr = None if addr == "-" else addr
        if addr and ("@" not in addr or "." not in addr.split("@")[-1]):
            sys.exit(f"'{addr}' is not a valid e-mail address")
        if addr and con.execute("SELECT 1 FROM users WHERE lower(email)=? AND username<>?", (addr, user)).fetchone():
            sys.exit(f"{addr} is already linked to another account")
        with con:
            n = con.execute("UPDATE users SET email=? WHERE username=?", (addr, user)).rowcount
        print(f"{user} -> {addr or '(no e-mail)'}" if n else f"No account '{user}'")
        return
    if args[0] == "delete" and len(args) == 2:
        user = args[1].lower()
        u = con.execute("SELECT id, name, role FROM users WHERE username=?", (user,)).fetchone()
        if not u:
            sys.exit(f"No account '{user}'")
        if u[2] == "admin" and con.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0] <= 1:
            sys.exit("This is the only administrator; make someone else administrator first.")
        n = con.execute("SELECT COUNT(*) FROM answers WHERE user_id=?", (u[0],)).fetchone()[0]
        with con:
            for t in ("sessions", "progress", "answers", "module_users"):
                con.execute(f"DELETE FROM {t} WHERE user_id=?", (u[0],))
            con.execute("DELETE FROM users WHERE id=?", (u[0],))
        print(f"Deleted {user} ({u[1]}) and {n} answers")
        return
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
