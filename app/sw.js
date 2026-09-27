// Orora AgriTech — service worker: cache everything needed to run with no network.
// Bump VERSION whenever app files or the model change.
const VERSION = "orora-v0.1";
const SHELL = [
  "./", "index.html", "styles.css", "app.js", "config.js", "i18n.js",
  "manifest.webmanifest", "icon.svg",
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.22.0/dist/tf.min.js",
];

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    await cache.addAll(SHELL);
    // Model: model.json plus every weight shard it lists. Missing model = app still installs.
    try {
      const res = await fetch("model/model.json", { cache: "no-cache" });
      if (res.ok) {
        const json = await res.clone().json();
        await cache.put("model/model.json", res);
        const shards = (json.weightsManifest || []).flatMap(g => g.paths).map(p => "model/" + p);
        await cache.addAll([...shards, "model/labels.json"].filter(Boolean));
      }
    } catch (e) { /* no model yet */ }
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
