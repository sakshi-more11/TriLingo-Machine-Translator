const API_BASE = ""; // same-origin (FastAPI serves this frontend)

const srcLangSelect = document.getElementById("srcLangSelect");
const tgtLangSelect = document.getElementById("tgtLangSelect");
const swapBtn = document.getElementById("swapBtn");
const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const inputHint = document.getElementById("inputHint");
const translateBtn = document.getElementById("translateBtn");
const statusMsg = document.getElementById("statusMsg");
const micBtn = document.getElementById("micBtn");
const speakBtn = document.getElementById("speakBtn");
const confidenceValue = document.getElementById("confidenceValue");
const confidenceFill = document.getElementById("confidenceFill");
const ttsAudio = document.getElementById("ttsAudio");

const LANG_NAMES = { en: "English", hi: "Hindi", mr: "Marathi" };

let lastTranslation = "";
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

outputText.textContent = "Your translation will appear here...";
outputText.classList.add("placeholder");

// ---------- Custom dropdown ----------
function initDropdown(root) {
  const trigger = root.querySelector(".select-trigger");
  const label = root.querySelector(".select-label");
  const options = root.querySelectorAll(".select-options li");

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    document.querySelectorAll(".lang-select.open").forEach((el) => {
      if (el !== root) el.classList.remove("open");
    });
    root.classList.toggle("open");
  });

  options.forEach((opt) => {
    opt.addEventListener("click", () => {
      const value = opt.dataset.value;
      root.dataset.value = value;
      label.textContent = LANG_NAMES[value];
      options.forEach((o) => o.classList.toggle("active", o === opt));
      root.classList.remove("open");
    });
  });
}

initDropdown(srcLangSelect);
initDropdown(tgtLangSelect);

document.addEventListener("click", () => {
  document.querySelectorAll(".lang-select.open").forEach((el) => el.classList.remove("open"));
});

function getLang(select) {
  return select.dataset.value;
}
function setLang(select, value) {
  select.dataset.value = value;
  select.querySelector(".select-label").textContent = LANG_NAMES[value];
  select.querySelectorAll(".select-options li").forEach((o) => {
    o.classList.toggle("active", o.dataset.value === value);
  });
}

// ---------- Status / loading helpers ----------
function setStatus(msg, isError = true) {
  statusMsg.textContent = msg || "";
  statusMsg.style.color = isError ? "#f87171" : "#2cb67d";
}

function setLoading(loading) {
  translateBtn.classList.toggle("loading", loading);
  translateBtn.disabled = loading;
}

function setConfidence(pct) {
  const val = typeof pct === "number" ? pct : 0;
  confidenceFill.style.width = `${val}%`;
  confidenceValue.textContent = typeof pct === "number" ? `${val.toFixed(1)}%` : "—";
}

// Typewriter-style reveal for the translated text
function revealText(el, text) {
  el.classList.remove("placeholder");
  el.innerHTML = "";
  const frag = document.createDocumentFragment();
  [...text].forEach((ch, i) => {
    const span = document.createElement("span");
    span.className = "char";
    span.style.animationDelay = `${Math.min(i * 12, 600)}ms`;
    span.textContent = ch;
    frag.appendChild(span);
  });
  el.appendChild(frag);
}

// ---------- Swap languages ----------
swapBtn.addEventListener("click", () => {
  const s = getLang(srcLangSelect);
  const t = getLang(tgtLangSelect);
  setLang(srcLangSelect, t);
  setLang(tgtLangSelect, s);

  const inVal = inputText.value;
  inputText.value = lastTranslation || "";
  lastTranslation = inVal;
});

// ---------- Translate ----------
async function translate() {
  const text = inputText.value.trim();
  if (!text) {
    setStatus("Type or speak something first.");
    return;
  }
  const src_lang = getLang(srcLangSelect);
  const tgt_lang = getLang(tgtLangSelect);
  if (src_lang === tgt_lang) {
    setStatus("Source and target languages must differ.");
    return;
  }

  setStatus("Translating... (first request after starting the server can take a while while the model loads)", false);
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/api/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, src_lang, tgt_lang }),
    });
    if (!res.ok) {
      const errBody = await res.text();
      throw new Error(`Server error (${res.status}): ${errBody.slice(0, 200)}`);
    }
    const data = await res.json();

    lastTranslation = data.translation;
    revealText(outputText, data.translation);
    setConfidence(data.confidence);
    setStatus("");

    inputHint.textContent = data.was_transliterated
      ? `Detected Hinglish → converted to native script: "${data.source_text_used}"`
      : "";
  } catch (err) {
    setStatus(`Translation failed: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

translateBtn.addEventListener("click", translate);
inputText.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) translate();
});

// ---------- Text-to-speech playback ----------
speakBtn.addEventListener("click", async () => {
  const text = lastTranslation.trim();
  if (!text) {
    setStatus("Nothing to speak yet — translate something first.");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/api/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, lang: getLang(tgtLangSelect) }),
    });
    if (!res.ok) throw new Error(`Server error (${res.status})`);
    const blob = await res.blob();
    ttsAudio.src = URL.createObjectURL(blob);
    ttsAudio.play();
  } catch (err) {
    setStatus(`Playback failed: ${err.message}`);
  }
});

// ---------- Speech-to-translation (mic input) ----------
micBtn.addEventListener("click", async () => {
  if (isRecording) {
    mediaRecorder.stop();
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      isRecording = false;
      micBtn.classList.remove("recording");
      stream.getTracks().forEach((t) => t.stop());

      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      await sendSpeechForTranslation(audioBlob);
    };

    mediaRecorder.start();
    isRecording = true;
    micBtn.classList.add("recording");
    setStatus("Listening... click the mic again to stop.", false);
  } catch (err) {
    setStatus(`Microphone access denied: ${err.message}`);
  }
});

async function sendSpeechForTranslation(audioBlob) {
  setLoading(true);
  setStatus("Transcribing and translating...", false);

  const form = new FormData();
  form.append("audio", audioBlob, "speech.webm");
  form.append("src_lang", getLang(srcLangSelect));
  form.append("tgt_lang", getLang(tgtLangSelect));

  try {
    const res = await fetch(`${API_BASE}/api/speech-translate`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      const errBody = await res.text();
      throw new Error(`Server error (${res.status}): ${errBody.slice(0, 200)}`);
    }
    const data = await res.json();

    inputText.value = data.transcript;
    lastTranslation = data.translation;
    revealText(outputText, data.translation);
    setConfidence(data.confidence);
    setStatus("");

    inputHint.textContent = data.was_transliterated
      ? "Detected Hinglish speech → converted to native script before translating."
      : "";
  } catch (err) {
    setStatus(`Speech translation failed: ${err.message}`);
  } finally {
    setLoading(false);
  }
}
