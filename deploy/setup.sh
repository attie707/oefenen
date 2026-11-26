#!/usr/bin/env bash
# Installs or updates the Oefenen platform INSIDE the LXC (run as root). Safe to run again and again.
# On the first run it imports the old frans-oefenen / nederlands-oefenen apps and switches them off.
set -euo pipefail
export LANG=C.UTF-8 LC_ALL=C.UTF-8 DEBIAN_FRONTEND=noninteractive

APP=oefenen
APP_USER=oefenen
PORT=8080
DIR=/opt/$APP
DATA=/var/lib/$APP
# Piper voices used by the subjects:  <path on huggingface>/<voice name>
VOICES="fr/fr_FR/siwis/medium/fr_FR-siwis-medium nl/nl_BE/nathalie/medium/nl_BE-nathalie-medium"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m %s\n' "$*"; }

# ---- packages ----
missing=()
for p in python3 python3-venv git ca-certificates curl; do dpkg -s "$p" >/dev/null 2>&1 || missing+=("$p"); done
if [ ${#missing[@]} -gt 0 ]; then
  say "Installing ${missing[*]}"
  apt-get update -qq && apt-get install -y -qq "${missing[@]}" >/dev/null
fi

# ---- user + data ----
id "$APP_USER" >/dev/null 2>&1 || useradd --system --home "$DATA" --shell /usr/sbin/nologin "$APP_USER"
mkdir -p "$DATA"

# ---- one-time move from the old separate apps ----
if [ ! -f "$DATA/oefenen.db" ]; then
  mkdir -p "$DATA/legacy"
  for old in frans nederlands; do
    svc=$old-oefenen
    if systemctl list-unit-files "$svc.service" >/dev/null 2>&1 && systemctl is-enabled --quiet "$svc" 2>/dev/null; then
      say "Stopping old app $svc (its data stays in /var/lib/$svc)"
      systemctl disable --now "$svc" >/dev/null 2>&1 || true
    fi
    if [ -f "/var/lib/$svc/$old.db" ]; then
      python3 -c "import sqlite3,sys;s=sqlite3.connect(sys.argv[1]);d=sqlite3.connect(sys.argv[2]);s.backup(d)" \
        "/var/lib/$svc/$old.db" "$DATA/legacy/$old.db"
      [ -d "/var/lib/$svc/audio" ] && mkdir -p "$DATA/$old" && cp -rn "/var/lib/$svc/audio" "$DATA/$old/" || true
      say "Copied the $old data for import"
    fi
  done
fi
chown -R "$APP_USER": "$DATA"

# ---- Piper (local, free speech) ----
if ! /opt/piper/bin/python -c "import piper" >/dev/null 2>&1; then
  say "Installing Piper speech engine (one time, ~1-2 minutes)"
  python3 -m venv /opt/piper
  /opt/piper/bin/pip install -q --upgrade pip && /opt/piper/bin/pip install -q piper-tts \
    && say "Piper installed" || warn "Piper could not be installed. The app still works with the browser voice."
fi
mkdir -p /opt/piper/voices
for v in $VOICES; do
  name=$(basename "$v")
  for ext in onnx onnx.json; do
    f=/opt/piper/voices/$name.$ext
    if [ ! -s "$f" ]; then
      say "Downloading voice $name.$ext"
      curl -fsSL -o "$f.tmp" "https://huggingface.co/rhasspy/piper-voices/resolve/main/$v.$ext" \
        && mv "$f.tmp" "$f" || { rm -f "$f.tmp"; warn "Voice download failed; the browser voice will be used."; }
    fi
  done
done

# ---- settings file (Azure speech and https cookie are optional) ----
if [ ! -f /etc/oefenen-tts.env ]; then
  cat > /etc/oefenen-tts.env <<'ENV'
# Settings for the Oefenen platform. Run 'update' after changing this file.
# Optional: Microsoft Azure neural voices (most natural). Free tier F0 = 500,000 characters/month.
#AZURE_TTS_KEY=paste-your-key-here
#AZURE_TTS_REGION=westeurope
# Only when the site is reached through https (Nginx Proxy Manager / Cloudflare):
#COOKIE_SECURE=1
ENV
  chmod 600 /etc/oefenen-tts.env
fi

# ---- service ----
cat > /etc/systemd/system/$APP.service <<UNIT
[Unit]
Description=Oefenen learning platform
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
WorkingDirectory=$DIR/app
Environment=DATA_DIR=$DATA PORT=$PORT QUIET=1 PIPER_VOICES=/opt/piper/voices
Environment=LEGACY_DBS=frans=$DATA/legacy/frans.db,nederlands=$DATA/legacy/nederlands.db
EnvironmentFile=-/etc/oefenen-tts.env
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
RestartSec=3
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
UNIT

# ---- helper commands ----
cat > /usr/local/bin/update.new <<'UPD'
#!/usr/bin/env bash
# Updates the Oefenen platform from GitHub. Accounts and scores are kept.
set -e
export LANG=C.UTF-8 LC_ALL=C.UTF-8
git -C /opt/oefenen pull --ff-only
bash /opt/oefenen/deploy/setup.sh
UPD
cat > /usr/local/bin/backup.new <<'BAK'
#!/usr/bin/env bash
# Copies the database to /root (safe while running).
set -e
out=/root/oefenen-$(date +%F).db
python3 -c "import sqlite3,sys;s=sqlite3.connect(sys.argv[1]);d=sqlite3.connect(sys.argv[2]);s.backup(d)" /var/lib/oefenen/oefenen.db "$out"
echo "Backup: $out"
BAK
chmod +x /usr/local/bin/update.new /usr/local/bin/backup.new
mv -f /usr/local/bin/update.new /usr/local/bin/update
mv -f /usr/local/bin/backup.new /usr/local/bin/backup
ln -sf /usr/local/bin/update /usr/sbin/update
ln -sf /usr/local/bin/backup /usr/sbin/backup

systemctl daemon-reload
systemctl enable "$APP" >/dev/null 2>&1
systemctl restart "$APP"
sleep 3
if systemctl is-active --quiet "$APP"; then
  journalctl -u "$APP" -n 30 --no-pager -o cat | grep -E '^(Imported|Speech|Oefenen)' | sort -u || true
  say "Oefenen is running on port $PORT"
else
  warn "$APP did not start. See: journalctl -u $APP -n 50"
  exit 1
fi
mem=$(awk '/MemTotal/{print int($2/1024)}' /proc/meminfo)
[ "$mem" -ge 900 ] || warn "This container has ${mem} MB RAM. For Piper speech give it 1024 MB (on the Proxmox host: pct set <ID> --memory 1024)."
