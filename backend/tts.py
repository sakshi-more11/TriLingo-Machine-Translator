"""
tts.py
------
Text-to-speech using gTTS. Completes the voice-to-voice loop:
translated text -> spoken audio the user can play back instantly.

Swap in Coqui TTS (better quality, on-device, no internet needed
at inference time) if you want to remove the Google Translate TTS
dependency later -- the `synthesize()` contract stays the same.
"""

import io

from gtts import gTTS

# gTTS language codes for our three languages
TTS_LANG_MAP = {"en": "en", "hi": "hi", "mr": "mr"}


def synthesize(text: str, lang: str) -> bytes:
    """Convert `text` to speech and return raw MP3 bytes."""
    if lang not in TTS_LANG_MAP:
        raise ValueError(f"Unsupported TTS language: {lang}")

    buf = io.BytesIO()
    tts = gTTS(text=text, lang=TTS_LANG_MAP[lang])
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()
