"""Text-to-speech with a cache, shared by all subjects.

Engines, best first (each one only if configured); if one fails, the next one is used:
  1. Google Gemini TTS  - GEMINI_API_KEY            (most natural; also Ukrainian, French, Dutch)
  2. Azure neural       - AZURE_TTS_KEY + AZURE_TTS_REGION
  3. Piper (local)      - /opt/piper with a voice for the language
  4. nothing            - the browser reads aloud itself
Every sound is generated once and stored in DATA_DIR/<subject>/audio.
Only texts that occur in the app (allowed) are spoken, so nobody can use up your quota.

Optional settings: GEMINI_TTS_MODEL (default below), GEMINI_TTS_VOICE (default Kore),
GEMINI_TTS_STYLE (optional style instruction placed before the text; off by default, because with short
words Gemini sometimes reads the instruction aloud), TTS_ENGINE=gemini|azure|piper.
"""
import base64
import hashlib
import json
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
import wave
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
GEMINI_BASE = os.environ.get("GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta")
# tried in this order; a model that doesn't exist (404) is skipped automatically
GEMINI_MODELS = [m for m in [os.environ.get("GEMINI_TTS_MODEL", "").strip(), "gemini-3.8-flash-tts",
                             "gemini-3.8-flash-tts-preview", "gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"] if m]
LANG_NAMES = {"uk": "Ukrainian", "fr": "French", "nl": "Dutch", "en": "English"}
GEMINI_CACHE = "g2"          # bump to make all Gemini sounds again


class TTS:
    def __init__(self, data_dir, lang, azure_voice, allowed, piper_voice=None):
        self.dir = os.path.join(data_dir, "audio")
        os.makedirs(self.dir, exist_ok=True)
        self.lang = lang
        self.allowed = set(allowed)
        self.lock = threading.Lock()
        self.worker = None
        self.cooldown = {}                       # engine -> time until which we don't try it
        self.failures = 0
        # Gemini
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.gemini_models = list(GEMINI_MODELS)
        self.gemini_voice = os.environ.get("GEMINI_TTS_VOICE", "Kore").strip()
        style = os.environ.get("GEMINI_TTS_STYLE", "").strip()
        self.gemini_style = "" if style in ("", "-") else style.replace("{language}", LANG_NAMES.get(lang[:2], ""))
        self.gemini_lang_code = True
        # Azure
        self.azure_key = os.environ.get("AZURE_TTS_KEY", "").strip()
        self.azure_region = os.environ.get("AZURE_TTS_REGION", "westeurope").strip()
        self.azure_voice = azure_voice
        # Piper
        self.piper_py = os.environ.get("PIPER_PYTHON", "/opt/piper/bin/python")
        voices = os.environ.get("PIPER_VOICES", "/opt/piper/voices")
        self.piper_model = os.path.join(voices, piper_voice + ".onnx") if piper_voice else os.environ.get("PIPER_MODEL", "")

        want = os.environ.get("TTS_ENGINE", "auto").lower()
        self.engines = []
        if want in ("auto", "gemini") and self.gemini_key:
            self.engines.append("gemini")
        if want in ("auto", "azure") and self.azure_key:
            self.engines.append("azure")
        if os.path.exists(self.piper_py) and os.path.exists(self.piper_model):
            self.engines.append("piper")             # always kept as a fallback when installed
        self.engine = self.engines[0] if self.engines else None
        if "gemini" in self.engines:
            self._clean_old_gemini()
        desc = ", then ".join(f"{e} ({self._voice(e)})" for e in self.engines) or "browser"
        print(f"Speech {lang}: {desc}", flush=True)

    def _clean_old_gemini(self):
        """One time: remove Gemini sounds made with the old spoken instruction (24 kHz WAVs without the g2 tag)."""
        marker = os.path.join(self.dir, ".gemini-" + GEMINI_CACHE)
        if os.path.exists(marker):
            return
        n = 0
        for f in os.listdir(self.dir):
            if f.endswith(".wav"):
                try:
                    with wave.open(os.path.join(self.dir, f)) as w:
                        rate = w.getframerate()
                    if rate == 24000:                # Gemini; Piper voices are 22.05 kHz
                        os.remove(os.path.join(self.dir, f))
                        n += 1
                except Exception:  # noqa
                    pass
        open(marker, "w").close()
        if n:
            print(f"Speech {self.lang}: removed {n} old Gemini sounds, they will be made again", flush=True)

    def _voice(self, engine):
        return {"gemini": self.gemini_voice + "-" + GEMINI_CACHE, "azure": self.azure_voice,
                "piper": os.path.basename(self.piper_model)}.get(engine, "")

    # ---------- cache ----------
    def _path(self, text, engine):
        h = hashlib.sha1(f"{engine}|{self._voice(engine)}|{text}".encode()).hexdigest()[:20]
        return os.path.join(self.dir, h + (".mp3" if engine == "azure" else ".wav"))

    def cached(self, text):
        return any(os.path.exists(self._path(text, e)) for e in self.engines[:1])

    def get(self, text, engines=None):
        """Returns (bytes, mimetype), or None (then the browser reads aloud itself)."""
        if not self.engines or text not in self.allowed:
            return None
        for eng in engines or self.engines:
            path = self._path(text, eng)
            if not os.path.exists(path):
                if self.cooldown.get(eng, 0) > time.time():
                    continue
                with self.lock:
                    if not os.path.exists(path) and not self._synth(eng, text, path):
                        continue
            with open(path, "rb") as f:
                return f.read(), ("audio/mpeg" if path.endswith(".mp3") else "audio/wav")
        return None

    def _synth(self, eng, text, path):
        try:
            {"gemini": self._gemini, "azure": self._azure, "piper": self._piper}[eng](text, path)
            if eng == self.engine:
                self.failures = 0
            return os.path.exists(path)
        except RateLimited as e:
            self.cooldown[eng] = time.time() + e.wait
            print(f"Speech {self.lang}: {eng} limit reached, pausing {e.wait // 60} min ({e})", flush=True)
            return False
        except Exception as e:  # noqa
            if eng == self.engine:
                self.failures += 1
            print(f"Speech {self.lang}: {eng} failed for '{text[:30]}': {e}", flush=True)
            return False

    # ---------- Google Gemini ----------
    def _gemini(self, text, path):
        prompt = f"{self.gemini_style} {text}" if self.gemini_style else text
        last = None
        for model in list(self.gemini_models):
            speech = {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": self.gemini_voice}}}
            if self.gemini_lang_code:
                speech["languageCode"] = self.lang
            body = {"contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": speech}}
            req = urllib.request.Request(f"{GEMINI_BASE}/models/{model}:generateContent", data=json.dumps(body).encode(),
                                         method="POST", headers={"x-goog-api-key": self.gemini_key,
                                                                 "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read())
            except urllib.error.HTTPError as e:
                raw = e.read().decode(errors="replace")
                try:                                  # Google's errors are JSON: keep only the message
                    msg = json.loads(raw)["error"]["message"]
                except Exception:  # noqa
                    msg = " ".join(raw.split())
                msg = msg[:300]
                if e.code == 429:
                    raise RateLimited(msg, 600)
                if e.code == 404:                     # model not available: try the next one
                    self.gemini_models.remove(model)
                    last = f"{model}: not found"
                    continue
                if e.code == 400 and "languageCode" in msg and self.gemini_lang_code:
                    self.gemini_lang_code = False    # older models: let Gemini detect the language
                    return self._gemini(text, path)
                if e.code in (401, 403) or (e.code == 400 and "API key" in msg):
                    raise RateLimited(f"key refused: {msg}", 3600)
                raise RuntimeError(f"HTTP {e.code}: {msg}")
            if self.gemini_models[0] != model:
                self.gemini_models.remove(model)
                self.gemini_models.insert(0, model)
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            audio = next((p["inlineData"] for p in parts if "inlineData" in p), None)
            if not audio:
                raise RuntimeError("no audio in the answer")
            pcm = base64.b64decode(audio["data"])
            rate = int((re.search(r"rate=(\d+)", audio.get("mimeType", "")) or [0, 24000])[1])
            seconds = len(pcm) / 2 / rate
            if seconds > 2.5 + len(text) / 4:        # much longer than the text: it said something extra
                if self.gemini_style:
                    self.gemini_style = ""           # drop the instruction and try once more with the bare text
                    return self._gemini(text, path)
                raise RuntimeError(f"audio too long ({seconds:.1f}s for {len(text)} characters), not saved")
            tmp = path + ".tmp"
            with wave.open(tmp, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(pcm)
            os.replace(tmp, path)
            return
        raise RuntimeError(last or "no Gemini TTS model available")

    # ---------- Azure ----------
    def _azure(self, text, path):
        ssml = (f"<speak version='1.0' xml:lang='{self.lang}'><voice name='{self.azure_voice}'>"
                f"<prosody rate='-8%'>{escape(text)}</prosody></voice></speak>")
        req = urllib.request.Request(
            f"https://{self.azure_region}.tts.speech.microsoft.com/cognitiveservices/v1",
            data=ssml.encode(), method="POST", headers={
                "Ocp-Apim-Subscription-Key": self.azure_key, "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3", "User-Agent": "oefenen-app"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise RateLimited("Azure quota", 600)
            raise
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)

    # ---------- Piper (local) ----------
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
                raise RuntimeError(reply or "worker stopped")
            except (BrokenPipeError, OSError):
                self.worker = None
                if attempt:
                    raise

    # ---------- prepare everything in the background ----------
    def prewarm(self):
        if not self.engine:
            return
        # Gemini: gently (free tier has request limits); local engines: as fast as possible
        gap = 6.5 if self.engine == "gemini" else 0.05

        def run():
            time.sleep(3)
            todo = [t for t in sorted(self.allowed) if not os.path.exists(self._path(t, self.engine))]
            if not todo:
                return
            print(f"Speech {self.lang}: preparing {len(todo)} sounds with {self.engine}...", flush=True)
            done = 0
            for t in todo:
                while self.cooldown.get(self.engine, 0) > time.time():
                    time.sleep(30)
                if self.failures >= 5:
                    print(f"Speech {self.lang}: too many errors with {self.engine}, stopped preparing "
                          f"(sounds are made when needed)", flush=True)
                    return
                with self.lock:
                    if not os.path.exists(self._path(t, self.engine)):
                        self._synth(self.engine, t, self._path(t, self.engine))
                if os.path.exists(self._path(t, self.engine)):
                    done += 1
                time.sleep(gap)
            print(f"Speech {self.lang}: {done} of {len(todo)} sounds ready ({self.engine})", flush=True)
        threading.Thread(target=run, daemon=True).start()


class RateLimited(Exception):
    def __init__(self, msg, wait):
        super().__init__(msg)
        self.wait = wait
