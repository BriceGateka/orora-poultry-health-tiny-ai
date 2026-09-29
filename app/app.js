// Orora AgriTech — offline droppings check (demo).
// Flow: photo -> on-device model -> result + advice -> SMS to vet -> saved batch record.
import { CONFIG } from "./config.js";
import { STRINGS, LEVEL, t, hasFullTranslation } from "./i18n.js";

const $ = sel => document.querySelector(sel);
const params = new URLSearchParams(location.search);
const MOCK = params.get("mock") === "1";           // UI test mode: random output, loudly labelled
const CACHE_EDGE = 320;                              // same downscale as the training cache

const store = {
  get(key, fallback) { try { const v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage blocked: app still works */ } },
};

const state = {
  lang: store.get("orora.lang", "en"),
  model: null,
  meta: { classes: CONFIG.defaultClasses, size: CONFIG.defaultSize, threshold: CONFIG.defaultThreshold },
  last: null,
};

// ------------------------------------------------------------------ language
function applyLang() {
  document.documentElement.lang = state.lang === "rn" ? "rn" : state.lang;
  $("#lang").value = state.lang;
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(state.lang, el.dataset.i18n); });
  $("#lang-banner").hidden = hasFullTranslation(state.lang);
  $("#lang-banner").textContent = t(state.lang, "langFallback");
  $("#mock-banner").hidden = !MOCK;
  $("#mock-banner").textContent = t(state.lang, "mockBanner");
  updateNet();
  setModelStatus();
  if (state.last) renderResult(state.last);
  renderRecords();
}
$("#lang").addEventListener("change", e => { state.lang = e.target.value; store.set("orora.lang", state.lang); applyLang(); });

// ------------------------------------------------------------------ network pill
function updateNet() {
  const el = $("#net");
  el.textContent = navigator.onLine ? t(state.lang, "online") : t(state.lang, "offline");
  el.classList.toggle("off", !navigator.onLine);
}
addEventListener("online", updateNet);
addEventListener("offline", updateNet);

// ------------------------------------------------------------------ model
let modelState = "loading";
function setModelStatus() {
  const key = MOCK ? "modelReady" : { loading: "modelLoading", ready: "modelReady", missing: "modelMissing" }[modelState];
  $("#model-status").textContent = MOCK ? "" : t(state.lang, key);
}

async function loadModel() {
  try {
    const r = await fetch(CONFIG.labelsUrl);
    if (r.ok) {
      const j = await r.json();
      state.meta = {
        classes: j.classes || CONFIG.defaultClasses,
        size: (j.input && j.input.size && j.input.size[0]) || CONFIG.defaultSize,
        threshold: j.confidence_threshold ?? CONFIG.defaultThreshold,
      };
    }
  } catch { /* use defaults */ }
  if (MOCK) { modelState = "ready"; setModelStatus(); return; }
  try {
    if (!window.tf) throw new Error("TensorFlow.js not loaded");
    if (CONFIG.modelUrl.endsWith(".tflite")) {
      if (!window.tflite) throw new Error("TFLite runtime not loaded");
      tflite.setWasmPath(CONFIG.tfliteWasm);
      state.model = await tflite.loadTFLiteModel(CONFIG.modelUrl);
    } else {
      state.model = await tf.loadGraphModel(CONFIG.modelUrl);
    }
    // warm-up so the first real photo is fast
    tf.tidy(() => state.model.predict(tf.zeros([1, state.meta.size, state.meta.size, 3])));
    modelState = "ready";
  } catch (e) {
    console.warn("Model not available:", e);
    modelState = "missing";
  }
  setModelStatus();
}

function downscale(img) {
  const scale = Math.min(1, CACHE_EDGE / Math.max(img.naturalWidth, img.naturalHeight));
  const c = document.createElement("canvas");
  c.width = Math.round(img.naturalWidth * scale);
  c.height = Math.round(img.naturalHeight * scale);
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
  return c;
}

async function classify(img) {
  const n = state.meta.classes.length;
  if (MOCK) {
    const raw = Array.from({ length: n }, () => Math.random() ** 3);
    const sum = raw.reduce((a, b) => a + b, 0);
    return raw.map(v => v / sum);
  }
  if (!state.model) throw new Error("model missing");
  const s = state.meta.size;
  const out = tf.tidy(() => {
    const x = tf.browser.fromPixels(downscale(img)).resizeBilinear([s, s]).toFloat().expandDims(0); // RGB 0-255
    return state.model.predict(x);
  });
  const probs = Array.from(await out.data());
  out.dispose();
  return probs;
}

// ------------------------------------------------------------------ result
function renderResult(r) {
  const L = state.lang;
  const labels = t(L, "labels"), names = t(L, "classNames"), advice = t(L, "advice");
  const level = LEVEL[r.key];
  $("#result-card").className = `card level-${level}`;
  $("#advice-card").className = `card advice level-${level}`;
  $("#result-title").textContent = labels[r.key];
  $("#result-conf").textContent = `${t(L, "confidence")}: ${Math.round(r.top * 100)}%`;

  const order = r.probs.map((p, i) => [p, i]).sort((a, b) => b[0] - a[0]);
  $("#bars").innerHTML = "";
  order.forEach(([p, i], k) => {
    const row = document.createElement("div");
    row.className = "bar-row" + (k === 0 ? " top" : "");
    const name = document.createElement("span"); name.textContent = names[state.meta.classes[i]] || state.meta.classes[i];
    const pct = document.createElement("span"); pct.className = "pct"; pct.textContent = `${Math.round(p * 100)}%`;
    const track = document.createElement("div"); track.className = "track";
    const fill = document.createElement("div"); fill.className = "fill"; fill.style.width = `${(p * 100).toFixed(1)}%`;
    track.append(fill); row.append(name, pct, track); $("#bars").append(row);
  });

  $("#advice").innerHTML = "";
  advice[r.key].forEach(line => { const li = document.createElement("li"); li.textContent = line; $("#advice").append(li); });

  const sms = $("#sms");
  sms.textContent = level === "urgent" ? t(L, "sendVetUrgent") : t(L, "sendVet");
  sms.classList.toggle("urgent", level === "urgent");
  const body = [
    t(L, "smsHeader"),
    r.batch ? `Batch: ${r.batch}` : null,
    `${labels[r.key]} (${Math.round(r.top * 100)}%)`,
    new Date(r.at).toLocaleString(),
    MOCK ? "TEST MODE - not a real result" : null,
  ].filter(Boolean).join(" | ");
  sms.href = `sms:${CONFIG.vetPhone}?body=${encodeURIComponent(body)}`;
}

function show(view) {
  ["capture", "result", "records"].forEach(v => { $(`#view-${v}`).hidden = v !== view; });
  document.querySelectorAll(".tabs button").forEach(b =>
    b.classList.toggle("active", b.dataset.view === view || (view === "result" && b.dataset.view === "capture")));
  scrollTo(0, 0);
}
document.querySelectorAll(".tabs button").forEach(b => b.addEventListener("click", () => show(b.dataset.view)));
$("#again").addEventListener("click", () => { $("#photo").value = ""; show("capture"); });

$("#photo").addEventListener("change", async e => {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  if (!MOCK && modelState !== "ready") { alert(t(state.lang, "modelMissing")); return; }
  const img = $("#preview");
  // wait on the load event: img.decode() can stay pending while the image is not displayed
  await new Promise(resolve => { img.onload = img.onerror = resolve; img.src = URL.createObjectURL(file); });
  $("#result-title").textContent = t(state.lang, "analysing");
  show("result");
  try {
    const probs = await classify(img);
    const iTop = probs.indexOf(Math.max(...probs));
    const top = probs[iTop];
    const key = top >= state.meta.threshold ? state.meta.classes[iTop] : "unclear";
    state.last = { key, top, probs, batch: $("#batch").value.trim(), at: Date.now(), mock: MOCK };
    renderResult(state.last);
    saveRecord(state.last);
  } catch (err) {
    console.error(err);
    alert(t(state.lang, "modelMissing"));
    show("capture");
  }
});

// ------------------------------------------------------------------ records
function saveRecord(r) {
  const recs = store.get("orora.records", []);
  recs.unshift({ at: r.at, batch: r.batch, result: r.key, confidence: +r.top.toFixed(3),
                 probs: Object.fromEntries(state.meta.classes.map((c, i) => [c, +r.probs[i].toFixed(3)])), mock: r.mock });
  store.set("orora.records", recs.slice(0, 500));
  renderRecords();
}

function renderRecords() {
  const L = state.lang, labels = t(L, "labels");
  const recs = store.get("orora.records", []);
  const list = $("#record-list");
  list.innerHTML = "";
  if (!recs.length) { const p = document.createElement("p"); p.className = "muted"; p.textContent = t(L, "noRecords"); list.append(p); return; }
  recs.forEach(r => {
    const d = document.createElement("div"); d.className = "record";
    const b = document.createElement("b"); b.textContent = labels[r.result] || r.result;
    const meta = document.createElement("div"); meta.className = "meta";
    meta.textContent = [new Date(r.at).toLocaleString(), r.batch && `Batch ${r.batch}`,
      `${Math.round(r.confidence * 100)}%`, r.mock && "TEST"].filter(Boolean).join(" · ");
    d.append(b, meta); list.append(d);
  });
}

$("#export").addEventListener("click", () => {
  const recs = store.get("orora.records", []);
  const cls = state.meta.classes;
  const rows = [["timestamp", "batch", "result", "confidence", ...cls.map(c => `p_${c}`), "test_mode"]];
  recs.forEach(r => rows.push([new Date(r.at).toISOString(), r.batch || "", r.result, r.confidence,
    ...cls.map(c => (r.probs || {})[c] ?? ""), r.mock ? "yes" : "no"]));
  const csv = rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  a.download = `orora_records_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
});

// ------------------------------------------------------------------ start
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(e => console.warn("SW", e));
applyLang();
loadModel();
