"""Command-line admin tool, run inside the container as:  oefenen-admin <command>

  oefenen-admin list                 show all accounts
  oefenen-admin reset <username>     give the account a new temporary password (must be changed at login)
  oefenen-admin role <username> <student|teacher|admin>
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
        rows = con.execute("SELECT id, username, name, role, must_change FROM users ORDER BY id").fetchall()
        print("%-4s %-18s %-22s %-8s %s" % ("id", "username", "name", "role", "must change password"))
        for r in rows:
            print("%-4s %-18s %-22s %-8s %s" % (r[0], r[1], r[2], r[3], "yes" if r[4] else "-"))
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
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
