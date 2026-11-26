"""Text-to-speech met cache. Gedeeld door frans-oefenen en nederlands-oefenen.

Volgorde (TTS_ENGINE=auto):
  1. Azure neural voices  - als AZURE_TTS_KEY en AZURE_TTS_REGION gezet zijn (beste kwaliteit)
  2. Piper (lokaal)       - als PIPER_PYTHON en PIPER_MODEL bestaan
  3. niets                - de browser leest dan zelf voor
Elk gegenereerd geluid wordt bewaard in DATA_DIR/audio, dus elke zin wordt maar één keer gemaakt.
Alleen teksten die in de app voorkomen (allowed) worden uitgesproken, zodat niemand je Azure-tegoed opmaakt.
"""
import hashlib
import json
import os
import subprocess
import threading
import time
import urllib.request
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))


class TTS:
    def __init__(self, data_dir, lang, azure_voice, allowed, piper_voice=None):
        self.dir = os.path.join(data_dir, "audio")
        os.makedirs(self.dir, exist_ok=True)
        self.lang = lang
        self.allowed = set(allowed)
        self.lock = threading.Lock()
        self.worker = None
        self.azure_key = os.environ.get("AZURE_TTS_KEY", "").strip()
        self.azure_region = os.environ.get("AZURE_TTS_REGION", "westeurope").strip()
        self.azure_voice = azure_voice
        self.piper_py = os.environ.get("PIPER_PYTHON", "/opt/piper/bin/python")
        voices = os.environ.get("PIPER_VOICES", "/opt/piper/voices")
        self.piper_model = os.path.join(voices, piper_voice + ".onnx") if piper_voice else os.environ.get("PIPER_MODEL", "")
        want = os.environ.get("TTS_ENGINE", "auto").lower()
        self.engine = None
        if want in ("auto", "azure") and self.azure_key:
            self.engine = "azure"
        elif want in ("auto", "piper") and os.path.exists(self.piper_py) and os.path.exists(self.piper_model):
            self.engine = "piper"
        self.voice = {"azure": self.azure_voice, "piper": os.path.basename(self.piper_model)}.get(self.engine)
        self.failures = 0
        print(f"Speech {lang}: {self.engine or 'browser'} {self.voice or ''}", flush=True)

    # ---------- cache ----------
    def _path(self, text):
        h = hashlib.sha1(f"{self.engine}|{self.voice}|{text}".encode()).hexdigest()[:20]
        return os.path.join(self.dir, h + (".mp3" if self.engine == "azure" else ".wav"))

    def get(self, text):
        """Geeft (bytes, mimetype) of None (dan valt de browser terug op zijn eigen stem)."""
        if not self.engine or text not in self.allowed:
            return None
        path = self._path(text)
        if not os.path.exists(path):
            with self.lock:
                if not os.path.exists(path):
                    ok = self._synth(text, path)
                    if not ok:
                        return None
        with open(path, "rb") as f:
            return f.read(), ("audio/mpeg" if path.endswith(".mp3") else "audio/wav")

    def _synth(self, text, path):
        try:
            if self.engine == "azure":
                self._azure(text, path)
            else:
                self._piper(text, path)
            self.failures = 0
            return os.path.exists(path)
        except Exception as e:  # noqa
            self.failures += 1
            print(f"Speech failed ({self.engine}): {e}", flush=True)
            return False

    # ---------- Azure ----------
    def _azure(self, text, path):
        ssml = (f"<speak version='1.0' xml:lang='{self.lang}'><voice name='{self.azure_voice}'>"
                f"<prosody rate='-8%'>{escape(text)}</prosody></voice></speak>")
        req = urllib.request.Request(
            f"https://{self.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1",
            data=ssml.encode(), method="POST", headers={
                "Ocp-Apim-Subscription-Key": self.azure_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
                "User-Agent": "oefenen-app"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)

    # ---------- Piper (lokaal) ----------
    def _piper(self, text, path):
        for attempt in range(2):
            if not self.worker or self.worker.poll() is not None:
                self.worker = subprocess.Popen(
                    [self.piper_py, os.path.join(HERE, "piper_worker.py"), self.piper_model],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
            try:
                self.worker.stdin.write(json.dumps({"text": text, "out": path}) + "\n")
                self.worker.stdin.flush()
                reply = self.worker.stdout.readline().strip()
                if reply == "ok":
                    return
                raise RuntimeError(reply or "worker gestopt")
            except (BrokenPipeError, OSError):
                self.worker = None
                if attempt:
                    raise

    # ---------- alles vooraf maken ----------
    def prewarm(self):
        if not self.engine:
            return

        def run():
            time.sleep(3)
            todo = [t for t in sorted(self.allowed) if not os.path.exists(self._path(t))]
            if todo:
                print(f"Speech {self.lang}: preparing {len(todo)} sounds...", flush=True)
            for t in todo:
                if self.failures >= 5:
                    print(f"Speech {self.lang}: too many errors, stopped preparing", flush=True)
                    return
                self.get(t)
                time.sleep(0.05)
            if todo:
                print(f"Speech {self.lang}: all sounds ready", flush=True)
        threading.Thread(target=run, daemon=True).start()
