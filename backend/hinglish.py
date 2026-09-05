"""
hinglish.py
-----------
Detects and converts code-mixed / romanized Hindi-Marathi text
("Hinglish", e.g. "kaise ho") into native Devanagari script
before it is sent to the translation engine.

Many Indian users type in Roman script rather than Devanagari --
handling this transparently is what makes the translator usable
in the real world instead of only on clean textbook input.

Uses `indic-transliteration` (pure Python, ITRANS-scheme rules) --
deliberately chosen over ML-based transliteration engines like
ai4bharat-transliteration, which pulls in `fairseq` and is
effectively unusable on modern Python/Windows setups. This trades
a little flexibility on very free-form spelling for something
that installs cleanly everywhere.
"""

import re

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Heuristic: if text is almost entirely ASCII letters (no Devanagari
# codepoints) but is being requested as hi/mr, treat it as Hinglish.
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")


def looks_like_hinglish(text: str, target_script_lang: str) -> bool:
    """target_script_lang: 'hi' or 'mr'. Returns True if text is
    Roman-script but destined for a Devanagari-script language."""
    if target_script_lang not in ("hi", "mr"):
        return False
    return not bool(_DEVANAGARI_RE.search(text))


def to_devanagari(text: str, lang: str) -> str:
    """Convert romanized Hinglish text to Devanagari script.
    Devanagari is shared by both Hindi and Marathi, so `lang` does
    not change the conversion. Falls back to the original text on
    failure."""
    try:
        return transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
    except Exception:
        return text

