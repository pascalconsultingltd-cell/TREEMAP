// Offline: the page fills this cache (see cacheForOffline in index.html); pages try the network briefly so updates arrive, everything else comes from the cache first
const CACHE = 'treemap-1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  if (e.request.mode === 'navigate') {
    // Page: network within 3 s (and keep a copy), else the stored copy, so weak signal doesn't hang
    e.respondWith(caches.open(CACHE).then(async c => {
      const net = fetch(e.request).then(r => { if (r.ok) c.put('index.html', r.clone()); return r; });
      const late = new Promise(res => setTimeout(res, 3000));
      const r = await Promise.race([net.catch(() => null), late]);
      return r || (await c.match('index.html')) || net;
    }));
  } else e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(n => { if (n.ok) { const copy = n.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return n; })));
});
