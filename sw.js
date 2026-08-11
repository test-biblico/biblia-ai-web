const CACHE = "biblia-ai-v1";
const SHELL = ["./", "manifest.webmanifest", "nvidia_config.js", "sw.js"];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) {
      // cachear lo que se pueda; no fallar si un recurso falta
      return Promise.allSettled(SHELL.map(function (u) {
        return c.add(u).catch(function () {});
      }));
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
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req).then(function (cached) {
      const network = fetch(req).then(function (resp) {
        const copy = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(req, copy); });
        return resp;
      }).catch(function () { return cached; });
      return cached || network;
    })
  );
});
