"""
translator.py
-------------
Core translation engine for TriLingo Machine Translator.

Upgraded from the original LSTM Seq2Seq baseline to a fine-tunable
Transformer model (Meta's NLLB-200, distilled 600M variant) which
natively supports English, Hindi and Marathi at production quality.

Swap MODEL_NAME below with a fine-tuned checkpoint (e.g. an
IndicTrans2 or NLLB checkpoint you fine-tuned yourself on
Samanantar / FLORES-200) once you have one -- the rest of the
pipeline (confidence scoring, API contract) stays identical.
"""

from functools import lru_cache
from typing import Dict, Tuple

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "facebook/nllb-200-distilled-600M"

# NLLB uses FLORES-200 language codes.
LANG_CODES: Dict[str, str] = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "mr": "mar_Deva",
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def _load_model() -> Tuple[AutoTokenizer, AutoModelForSeq2SeqLM]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(DEVICE)
    model.eval()
    return tokenizer, model


def translate(text: str, src_lang: str, tgt_lang: str, max_length: int = 200):
    """
    Translate `text` from src_lang -> tgt_lang.

    Returns:
        {
            "translation": str,
            "confidence": float (0-100, avg token probability),
        }
    """
    if src_lang not in LANG_CODES or tgt_lang not in LANG_CODES:
        raise ValueError(f"Unsupported language pair: {src_lang} -> {tgt_lang}")

    tokenizer, model = _load_model()
    tokenizer.src_lang = LANG_CODES[src_lang]

    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(DEVICE)
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(LANG_CODES[tgt_lang])

    with torch.no_grad():
        output = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=max_length,
            num_beams=3,  # fewer beams = noticeably faster on CPU, small quality trade-off
            return_dict_in_generate=True,
            output_scores=True,
        )

    translation = tokenizer.batch_decode(output.sequences, skip_special_tokens=True)[0]
    confidence = _sequence_confidence(output)

    return {"translation": translation, "confidence": confidence}


def _sequence_confidence(output) -> float:
    """
    Confidence = the length-normalized log-probability of the
    generated sequence, which `generate()` already computes for us
    as `sequences_scores` (this works correctly for both greedy and
    beam search, unlike walking `output.scores` manually -- beam
    search reorders beams at every step, so per-step token scores
    don't line up with the final chosen sequence).

    Converted to a 0-100 percentage for the UI's confidence bar.
    """
    scores = getattr(output, "sequences_scores", None)
    if scores is None or scores.numel() == 0:
        return 0.0

    avg_log_prob = scores[0].item()
    confidence = min(max(torch.exp(torch.tensor(avg_log_prob)).item(), 0.0), 1.0)
    return round(confidence * 100, 2)
