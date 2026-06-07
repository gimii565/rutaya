const CACHE_NAME = 'rutaya-v3';
const urlsToCache = [
    '/static/css/base.css',
    '/static/css/passenger.css',
    '/static/css/driver.css',
    '/static/css/admin.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames =>
            Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME)
                    .map(name => caches.delete(name))
            )
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            if (response) return response;
            return fetch(event.request).catch(() => {
                if (event.request.destination === 'document') {
                    return caches.match(event.request.url);
                }
            });
        })
    );
});

self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'RutaYa';
    const options = {
        body: data.body || 'Nueva notificación',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-72.png',
        vibrate: [200, 100, 200],
        data: { trip_id: data.trip_id },
        actions: [
            { action: 'ver', title: '👀 Ver solicitud' }
        ]
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    const trip_id = event.notification.data.trip_id;
    event.waitUntil(
        clients.openWindow('/driver/dashboard')
    );
});