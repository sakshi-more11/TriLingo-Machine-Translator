"""
main.py
-------
FastAPI backend for TriLingo Machine Translator.

Endpoints:
    POST /api/translate            text -> translated text + confidence
    POST /api/speech-translate     audio -> transcript -> translation + confidence
    POST /api/speak                text -> mp3 audio bytes (TTS)
    GET  /api/health                health check

Run:
    uvicorn backend.main:app --reload --port 8000

The frontend/ folder is mounted as static files at "/", so the
whole app (UI + API) is served from a single port.
"""

import os

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import asr, hinglish, translator, tts

app = FastAPI(title="TriLingo Machine Translator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranslateRequest(BaseModel):
    text: str
    src_lang: str  # "en" | "hi" | "mr"
    tgt_lang: str  # "en" | "hi" | "mr"


class SpeakRequest(BaseModel):
    text: str
    lang: str


@app.on_event("startup")
def _warm_up_models():
    print("Loading translation model (first run downloads ~2.5GB, please wait)...")
    translator._load_model()
    print("Translation model ready.")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/translate")
def translate_text(req: TranslateRequest):
    text = req.text

    # Transparently handle Hinglish / romanized input.
    was_transliterated = False
    if hinglish.looks_like_hinglish(text, req.src_lang):
        converted = hinglish.to_devanagari(text, req.src_lang)
        if converted != text:
            text = converted
            was_transliterated = True

    result = translator.translate(text, req.src_lang, req.tgt_lang)
    result["source_text_used"] = text
    result["was_transliterated"] = was_transliterated
    return result


@app.post("/api/speech-translate")
async def speech_translate(
    audio: UploadFile = File(...),
    src_lang: str = Form(...),
    tgt_lang: str = Form(...),
):
    audio_bytes = await audio.read()
    transcript = asr.transcribe(audio_bytes, language_hint=src_lang)

    text = transcript["text"]
    was_transliterated = False
    if hinglish.looks_like_hinglish(text, src_lang):
        converted = hinglish.to_devanagari(text, src_lang)
        if converted != text:
            text = converted
            was_transliterated = True

    result = translator.translate(text, src_lang, tgt_lang)
    result["transcript"] = transcript["text"]
    result["detected_language"] = transcript["detected_language"]
    result["was_transliterated"] = was_transliterated
    return result


@app.post("/api/speak")
def speak(req: SpeakRequest):
    audio_bytes = tts.synthesize(req.text, req.lang)
    return Response(content=audio_bytes, media_type="audio/mpeg")


# Serve the frontend as static files (index.html at "/")
_frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
