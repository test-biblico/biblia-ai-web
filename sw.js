const CACHE = "biblia-ai-v1";
const SHELL = ["/", "/manifest.webmanifest", "/icon-192.png", "/icon-512.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      return c.addAll(SHELL);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; }).map(function (k) {
          return caches.delete(k);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function (e) {
  const req = e.request;
  const url = new URL(req.url);
  // Solo manejar GET
  if (req.method !== "GET") return;
  // API: network-first, fallback a cache si falla
  if (url.pathname.startsWith("/api/")) {
    e.respondWith(
      fetch(req).catch(function () {
        return caches.match(req);
      })
    );
    return;
  }
  // Estáticos: cache-first con actualización en background
  e.respondWith(
    caches.match(req).then(function (cached) {
      const network = fetch(req).then(function (resp) {
        const copy = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); });
        return resp;
      });
      return cached || network;
    })
  );
});
