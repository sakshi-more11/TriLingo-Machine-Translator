"""
asr.py
------
Speech-to-text using OpenAI Whisper. Handles the "speech in" half
of the voice-to-voice translation pipeline: record audio in the
browser -> transcribe here -> feed the text into translator.py.
"""

import tempfile
from functools import lru_cache

import whisper

WHISPER_MODEL_SIZE = "base"  # tiny / base / small / medium / large

# Whisper language codes we care about
WHISPER_LANG_MAP = {"en": "en", "hi": "hi", "mr": "mr"}


@lru_cache(maxsize=1)
def _load_model():
    return whisper.load_model(WHISPER_MODEL_SIZE)


def transcribe(audio_bytes: bytes, language_hint: str | None = None) -> dict:
    """
    Transcribe raw audio bytes (wav/mp3/webm) to text.

    Returns: {"text": str, "detected_language": str}
    """
    model = _load_model()

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()

        options = {}
        if language_hint in WHISPER_LANG_MAP:
            options["language"] = WHISPER_LANG_MAP[language_hint]

        result = model.transcribe(tmp.name, **options)

    return {
        "text": result.get("text", "").strip(),
        "detected_language": result.get("language", "unknown"),
    }
