<div align="center">

# 🌐 TriLingo Machine Translator

### Real-time voice & text translation across English · Hindi · Marathi

<p>
  <img src="https://img.shields.io/badge/status-active-2cb67d?style=for-the-badge" />
  <img src="https://img.shields.io/badge/python-3.10%2B-7f5af0?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-ff8906?style=for-the-badge" />
</p>

<p>
  <img src="https://img.shields.io/badge/Transformer-NLLB--200-7f5af0?style=flat-square" />
  <img src="https://img.shields.io/badge/ASR-Whisper-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/TTS-gTTS-2cb67d?style=flat-square" />
  <img src="https://img.shields.io/badge/Hinglish-Aware-ff8906?style=flat-square" />
</p>

*Speak or type in English, Hindi, or Marathi — get an instant translation, hear it spoken back, and see exactly how confident the model is.*

</div>

---

## 🔎 Overview

TriLingo bridges the language gap between **English, Hindi, and Marathi** — through text *or* your voice. It was built to handle the way people actually communicate: mixed scripts, romanized "Hinglish" typing, and the need for a translation you can trust, not just read.

```
🎙️ Speech / ⌨️ Text
        │
        ▼
🔤 Hinglish Detection & Transliteration
        │
        ▼
🧠 Transformer Translation Engine (NLLB-200)
        │
        ▼
📊 Confidence Scoring   +   🔊 Spoken Output
```

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🎙️ | **Voice-to-voice translation** | Speak into the mic → Whisper transcribes → translated → spoken back to you |
| ⌨️ | **Instant text translation** | Clean, fast translation across all three languages |
| 🔤 | **Hinglish-aware** | Romanized input like `"kaise ho"` is auto-detected and converted to native Devanagari before translation |
| 📊 | **Confidence meter** | Every translation shows a live, animated confidence score — no black-box guessing |
| 🔁 | **One-click language swap** | Smooth animated swap between source and target |
| 🎨 | **Full-screen animated UI** | Glassmorphism cards, gradient backgrounds, pulse-animated mic — built to demo well |

---

## 🎬 Demo Flow

1. Pick your **From** and **To** languages
2. Type, or tap the mic and speak
3. Watch the translation appear with a live **confidence bar**
4. Tap **🔊** to hear it spoken back

> *(Add a screen recording / GIF here once deployed — this is the single highest-impact addition for a portfolio README.)*

---

## 🧠 Model Upgrade: LSTM Seq2Seq → Transformer

| | Original | Current |
|---|---|---|
| Architecture | LSTM Seq2Seq | Transformer — `facebook/nllb-200-distilled-600M` |
| Fine-tuning | — | Swappable for a checkpoint fine-tuned on Samanantar / FLORES-200, or **IndicTrans2** |
| Confidence scoring | ❌ | ✅ Token-level decoder probability |
| Hinglish handling | ❌ | ✅ AI4Bharat transliteration |
| Speech I/O | ❌ | ✅ Whisper (in) + gTTS (out) |

The engine in `backend/translator.py` is built so you can point `MODEL_NAME` at your own fine-tuned checkpoint without changing the API contract.

---

## 🛠️ Tech Stack

**Backend** — FastAPI · HuggingFace Transformers (NLLB-200) · OpenAI Whisper · gTTS · AI4Bharat Transliteration

**Frontend** — Vanilla HTML5 / CSS3 / JavaScript · MediaRecorder API for in-browser voice capture · custom animated glassmorphic design

**Serving** — Single FastAPI process serves both API and UI — Docker- and cloud-deploy ready (Render / HuggingFace Spaces / AWS)

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

# 4. Install ffmpeg (required by Whisper)
#    macOS:   brew install ffmpeg
#    Ubuntu:  sudo apt install ffmpeg
#    Windows: https://ffmpeg.org/download.html

# 5. Run
uvicorn backend.main:app --reload --port 8000
```

Open **`http://localhost:8000`** — UI and API are served together.

> ⚠️ First run downloads the NLLB-200 and Whisper model weights from HuggingFace (a few GB, needs internet). Cached locally after that.

---


Built by [Sakshi More](https://github.com/sakshi-more11)

</div>
