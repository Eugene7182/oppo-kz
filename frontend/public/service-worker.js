self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open('oppo-kz-static-v3');
    await cache.addAll(['/','/index.html']);
  })());
});

self.addEventListener('fetch', (event) => {
  event.respondWith((async () => {
    const cache = await caches.open('oppo-kz-static-v3');
    const cached = await cache.match(event.request);
    if (cached) return cached;
    const resp = await fetch(event.request);
    if (event.request.method === 'GET' && resp.status === 200) {
      cache.put(event.request, resp.clone());
    }
    return resp;
  })());
});

self.addEventListener('push', function(event) {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) {}
  const title = data.title || 'Уведомление';
  const body = data.body || '';
  const payload = data.data || {};
  const options = { body, icon: '/icons/icon-192.png', badge: '/icons/badge-72.png', data: payload };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = '/notifications';
  event.waitUntil(clients.matchAll({type:'window'}).then(windowClients => {
    for (const client of windowClients) { if ('focus' in client) { return client.focus(); } }
    if (clients.openWindow) return clients.openWindow(url);
  }));
});
