// Rede primeiro (dados sempre atuais); cache só como reserva sem conexão.
const C = "casa-nova-v1";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || !e.request.url.startsWith(self.location.origin)) return;
  e.respondWith(fetch(e.request).then(r => {
    const c = r.clone(); caches.open(C).then(x => x.put(e.request, c)); return r;
  }).catch(() => caches.match(e.request)));
});
