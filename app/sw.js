// Orora AgriTech: service worker. Caches everything needed to run with no network.
// Bump VERSION whenever app files or the model change.
const VERSION = "orora-v0.4";
const TFLITE = "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-tflite@0.0.1-alpha.10/";
const SHELL = [
  "./", "index.html", "styles.css", "app.js", "config.js", "i18n.js",
  "manifest.webmanifest", "icon.svg",
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js",
  TFLITE + "dist/tf-tflite.min.js",
  // the TFLite runtime picks the SIMD build where the phone supports it, else the plain one
  TFLITE + "wasm/tflite_web_api_cc_simd.js", TFLITE + "wasm/tflite_web_api_cc_simd.wasm",
  TFLITE + "wasm/tflite_web_api_cc.js", TFLITE + "wasm/tflite_web_api_cc.wasm",
];
const FALLBACK_MODEL = "orora_droppings_v0_fp16.tflite";   // used only if labels.json names no file

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    // cache: "reload" skips the browser's HTTP cache, so a new VERSION always gets fresh files
    const fresh = url => new Request(url, { cache: "reload" });
    await cache.addAll(SHELL.map(fresh));
    // The model file is the one labels.json names. A missing model must not stop the install.
    try {
      const res = await fetch(fresh("model/labels.json"));
      if (res.ok) {
        const meta = await res.clone().json();
        await cache.put("model/labels.json", res);
        await cache.add(fresh("model/" + (meta.file || FALLBACK_MODEL)));
      }
    } catch (e) { /* model not added yet */ }
    self.skipWaiting();
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) if (key !== VERSION) await caches.delete(key);
    self.clients.claim();
  })());
});

// Cache first; fall back to network and keep a copy of what came back.
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  event.respondWith((async () => {
    const cached = await caches.match(event.request, { ignoreSearch: true });
    if (cached) return cached;
    try {
      const res = await fetch(event.request);
      if (res.ok) (await caches.open(VERSION)).put(event.request, res.clone());
      return res;
    } catch (e) {
      if (event.request.mode === "navigate") return caches.match("index.html");
      throw e;
    }
  })());
});
