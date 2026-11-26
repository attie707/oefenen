"""Draait in de Piper-omgeving (/opt/piper). Houdt het stemmodel geladen en maakt wav-bestanden.
Protocol: één JSON-regel per verzoek {"text": ..., "out": ...} -> antwoord "ok" of "err ...".
"""
import json
import os
import sys
import wave

from piper import PiperVoice

voice = PiperVoice.load(sys.argv[1])

for line in sys.stdin:
    try:
        req = json.loads(line)
        tmp = req["out"] + ".tmp"
        with wave.open(tmp, "wb") as w:
            if hasattr(voice, "synthesize_wav"):      # piper-tts 1.3+
                voice.synthesize_wav(req["text"], w)
            else:                                     # piper-tts 1.2
                voice.synthesize(req["text"], w)
        os.replace(tmp, req["out"])
        print("ok", flush=True)
    except Exception as e:  # noqa
        print("err " + str(e).replace("\n", " "), flush=True)
