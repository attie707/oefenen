"""Single sign-on through Cloudflare Access (e.g. "Sign in with Google").

Cloudflare Access puts a signed token (JWT, RS256) in the header Cf-Access-Jwt-Assertion.
We verify the signature against Cloudflare's public keys, plus the audience, issuer and expiry,
and only then trust the e-mail address in it. Pure Python, no extra packages.

Settings (in /etc/oefenen-tts.env):
  CF_ACCESS_TEAM=yourteam.cloudflareaccess.com
  CF_ACCESS_AUD=<Application Audience (AUD) Tag of the Access application>
"""
import base64
import hashlib
import json
import os
import threading
import time
import urllib.request

TEAM = os.environ.get("CF_ACCESS_TEAM", "").strip().removeprefix("https://").rstrip("/")
AUD = os.environ.get("CF_ACCESS_AUD", "").strip()
CERTS_URL = os.environ.get("CF_ACCESS_CERTS_URL") or (f"https://{TEAM}/cdn-cgi/access/certs" if TEAM else "")
ENABLED = bool(TEAM and AUD)

_keys, _keys_t, _lock = {}, 0.0, threading.Lock()
# DER prefix of a PKCS#1 v1.5 DigestInfo for SHA-256
_SHA256_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def _b64(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _load_keys(force=False):
    global _keys, _keys_t
    with _lock:
        if _keys and not force and time.time() - _keys_t < 3600:
            return _keys
        with urllib.request.urlopen(CERTS_URL, timeout=10) as r:
            data = json.loads(r.read())
        keys = {}
        for k in data.get("keys", []):
            if k.get("kty") == "RSA":
                keys[k["kid"]] = (int.from_bytes(_b64(k["n"]), "big"), int.from_bytes(_b64(k["e"]), "big"))
        _keys, _keys_t = keys, time.time()
        return keys


def _rs256_ok(signing_input, sig, n, e):
    k = (n.bit_length() + 7) // 8
    if len(sig) != k:
        return False
    em = pow(int.from_bytes(sig, "big"), e, n).to_bytes(k, "big")
    t = _SHA256_PREFIX + hashlib.sha256(signing_input).digest()
    expected = b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t
    return em == expected


def email_from(token):
    """Returns the verified e-mail address in a Cloudflare Access token, or None."""
    if not ENABLED or not token or token.count(".") != 2:
        return None
    try:
        h64, p64, s64 = token.split(".")
        header, payload = json.loads(_b64(h64)), json.loads(_b64(p64))
        if header.get("alg") != "RS256":
            return None
        keys = _load_keys()
        if header.get("kid") not in keys:
            keys = _load_keys(force=True)
        n, e = keys[header["kid"]]
        if not _rs256_ok(f"{h64}.{p64}".encode(), _b64(s64), n, e):
            return None
        aud = payload.get("aud")
        if AUD not in (aud if isinstance(aud, list) else [aud]):
            return None
        if payload.get("iss") not in (f"https://{TEAM}", f"https://{TEAM}/"):
            return None
        now = time.time()
        if payload.get("exp", 0) < now or payload.get("nbf", 0) > now + 60:
            return None
        email = (payload.get("email") or "").strip().lower()
        return email or None
    except Exception:  # noqa  (bad token, network problem, ...): just no single sign-on
        return None
