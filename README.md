# TriLingo Machine Translator 🌐

Real-time, voice-enabled machine translation between **English, Hindi, and Marathi** — upgraded from an LSTM Seq2Seq baseline to a fine-tunable Transformer engine, with speech input/output, confidence scoring, and Hinglish (romanized) text support.

![status](https://img.shields.io/badge/status-active-2cb67d) ![python](https://img.shields.io/badge/python-3.10%2B-7f5af0) ![license](https://img.shields.io/badge/license-MIT-ff8906)

---

## What it does

TriLingo lets you translate between English, Hindi, and Marathi through text **or your voice**, and hear the result spoken back — while transparently handling the way Indians actually type (Hinglish / romanized script).

**Flow:** `Speech or Text → (Hinglish detection & transliteration) → Translation → Confidence score → Spoken output`

---

## ✨ Features

- **Text translation** across English ⇄ Hindi ⇄ Marathi with one click.
- **Voice-to-voice translation** — speak into the mic, get a spoken translation back (Whisper ASR → MT → TTS).
- **Hinglish / code-mixed handling** — romanized input like `"kaise ho"` is auto-detected and transliterated to native Devanagari before translation, instead of failing silently.
- **Confidence/uncertainty display** — every translation ships with a live confidence meter (average decoder token probability), so users know when to trust the output.
- **Language swap** with one click, animated UI.
- **Fully responsive, full-screen, animated interface** — glassmorphism cards, gradient backgrounds, pulse-animated mic recording, and smooth transitions.

---

## 🧠 Model upgrade: LSTM Seq2Seq → Transformer

| | Original | Upgraded |
|---|---|---|
| Architecture | LSTM Seq2Seq | Transformer (NLLB-200, 600M distilled) |
| Fine-tuning target | — | Swap in your own fine-tuned checkpoint (e.g. on Samanantar / FLORES-200) |
| Confidence scoring | ❌ | ✅ Token-level decoder probability |
| Hinglish handling | ❌ | ✅ Auto-transliteration via indic-transliteration |
| Speech I/O | ❌ | ✅ Whisper (ASR) + gTTS (TTS) |

The translation engine (`backend/translator.py`) is architected so you can drop in a checkpoint you fine-tuned yourself (e.g. **IndicTrans2**) without touching the API contract — just point `MODEL_NAME` at your model.

---

## 🛠️ Tech Stack

**Backend**
- FastAPI (REST API + static file serving)
- HuggingFace Transformers — `facebook/nllb-200-distilled-600M` (swappable for IndicTrans2 / mBART-50 / your own fine-tuned model)
- OpenAI Whisper — speech-to-text
- gTTS — text-to-speech
- indic-transliteration — Hinglish → Devanagari (ITRANS-scheme, pure Python)

**Frontend**
- Vanilla HTML5 / CSS3 / JavaScript (no framework overhead)
- Web Audio / MediaRecorder API for in-browser mic recording
- Fully custom animated, glassmorphic, full-screen UI

**Deployment-ready**
- Single FastAPI process serves both API and UI (`uvicorn backend.main:app`)
- Dockerizable, deployable to Render / HuggingFace Spaces / AWS

---

## 🚀 Setup

```bash
# 1. Clone
git clone https://github.com/sakshi-more11/TriLingo-Machine-Translator.git
cd TriLingo-Machine-Translator

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. (First run only) ffmpeg is required by Whisper for audio decoding
#    macOS:  brew install ffmpeg
#    Ubuntu: sudo apt install ffmpeg
#    Windows: https://ffmpeg.org/download.html

# 5. Run the app (serves UI + API together)
uvicorn backend.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

> First run will download the NLLB-200 and Whisper model weights from HuggingFace — this requires an internet connection and a few GB of disk space. Subsequent runs use the local cache.

---

## 📁 Project Structure

```
TriLingo-Machine-Translator/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── translator.py      # Transformer MT engine + confidence scoring
│   ├── asr.py              # Whisper speech-to-text
│   ├── tts.py               # gTTS text-to-speech
│   ├── hinglish.py         # Romanized-text detection & transliteration
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── README.md
└── .gitignore
```

---

## 🔮 Roadmap

- Fine-tune on **Samanantar** / **FLORES-200** and benchmark BLEU/chrF against the LSTM baseline
- Swap gTTS for **Coqui TTS** for offline, higher-quality speech synthesis
- Add batch/document translation
- Dockerfile + one-click HuggingFace Spaces deploy

---

## License

MIT
