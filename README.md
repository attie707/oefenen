# Oefenen

A small, self-hosted learning platform for the family: **one login, one start page, several subjects**.
It's pure Python with **no dependencies** and uses SQLite for storage, with natural speech through Piper (local) or Azure.

| Subject | For | What |
|---|---|---|
| 🇫🇷 French | Dutch-speaking pupils | être, avoir, -er verbs: quiz, spelling levels, listening/dictation, speed round |
| 🇳🇱 Dutch | beginners (A1–A2), all in Dutch | words with pictures (de/het), verbs in 3 tenses, word order, listening |

More subjects (Ukrainian, topography of Europe) are coming as modules in `app/modules/`.

## Roles
| Role | Can do |
|---|---|
| 🎒 Student | Practise and see their own scores |
| 👩‍🏫 Teacher / parent | See the progress of all students per subject, export CSV |
| 🔑 Administrator | Also add accounts, change roles, reset passwords |

Passwords need 10+ characters with a lowercase letter, a capital letter, a digit and a special character. New and reset
passwords are temporary and must be changed at the first login. Each user picks English or Dutch under **Settings**.

## Install

**Into an existing LXC** (e.g. container 108 that runs the old frans-/nederlands-oefenen apps). Run on the Proxmox host:
```bash
pct exec 108 -- bash -c "git clone -q https://github.com/attie707/oefenen /opt/oefenen && bash /opt/oefenen/deploy/setup.sh"
```
The first run imports all accounts and scores from the old apps, copies their sound files and switches the old
apps off. Their data stays untouched in `/var/lib/frans-oefenen` and `/var/lib/nederlands-oefenen`.

**New LXC from scratch** (Proxmox host shell):
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/attie707/oefenen/main/proxmox-lxc.sh)"
```

The platform runs on port **8080**. Point Nginx Proxy Manager or the Cloudflare Tunnel to `http://<container-ip>:8080`.

| Task | Command (Proxmox host) |
|---|---|
| Update | `pct exec 108 -- update` |
| Backup | `pct exec 108 -- backup` |
| Logs | `pct exec 108 -- journalctl -u oefenen -f` |

## Settings (`/etc/oefenen-tts.env` inside the container, then `update`)
- https is detected automatically (via the `X-Forwarded-Proto` header from Nginx Proxy Manager or Cloudflare)
- `AZURE_TTS_KEY=...` and `AZURE_TTS_REGION=westeurope` for the most natural voices (free tier is plenty, since sounds are cached)

## Log in with Google (Cloudflare Access)
Put Cloudflare Access (Zero Trust, free up to 50 users) with Google as login method in front of the public hostname,
then add to `/etc/oefenen-tts.env` and run `update`:
```
CF_ACCESS_TEAM=yourteam.cloudflareaccess.com
CF_ACCESS_AUD=<Application Audience (AUD) Tag>
```
Link each account to its Google address under **Admin → E-mail**. The app verifies Cloudflare's signed token
(RS256, audience, issuer, expiry) before it trusts the address. Password login keeps working on the local address.

## Adding a subject
Create `app/modules/<name>/__init__.py` (with `KEY`, `ICON`, `TITLE`, `DESC`, TTS voice, `MODE_NAMES`, `phrases()` and
`handle(action, ctx)`), add the page in `app/static/<name>/`, and list the module in `app/modules/__init__.py`.
