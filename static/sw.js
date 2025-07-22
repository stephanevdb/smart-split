// Service Worker for Smart Split PWA

// Cache configuration
const CACHE_PREFIX = 'smart-split-pwa';
const CACHE_VERSION = Date.now(); // Dynamic version based on timestamp
const CACHE_NAME = `${CACHE_PREFIX}-v${CACHE_VERSION}`;
const OFFLINE_URL = '/offline';

// Auto-refresh configuration - aggressive cache clearing
const CACHE_REFRESH_INTERVAL = 60 * 60 * 1000; // 1 hour (reduced from 24 hours)
const CACHE_ENTRY_MAX_AGE = 60 * 1000; // 1 minute max cache age
const LAST_CACHE_CLEAR_KEY = 'lastCacheClear';

// Files to cache for offline functionality
const STATIC_CACHE_URLS = [
    '/',
    '/offline',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json'
];

// Auto-refresh utility functions
async function getLastCacheClear() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const response = await cache.match(LAST_CACHE_CLEAR_KEY);
        if (response) {
            const timestamp = await response.text();
            return parseInt(timestamp, 10);
        }
    } catch (error) {
        console.log('Error getting last cache clear time:', error);
    }
    return 0;
}

async function setLastCacheClear(timestamp) {
    try {
        const cache = await caches.open(CACHE_NAME);
        const response = new Response(timestamp.toString());
        await cache.put(LAST_CACHE_CLEAR_KEY, response);
        console.log('Cache clear timestamp updated:', new Date(timestamp).toISOString());
    } catch (error) {
        console.log('Error setting last cache clear time:', error);
    }
}

async function shouldClearCache() {
    const lastClear = await getLastCacheClear();
    const now = Date.now();
    const timeSinceLastClear = now - lastClear;
    
    console.log(`Time since last cache clear: ${Math.round(timeSinceLastClear / (1000 * 60 * 60))} hours`);
    
    return timeSinceLastClear >= CACHE_REFRESH_INTERVAL;
}

async function clearAllCaches() {
    try {
        const cacheNames = await caches.keys();
        const deletionPromises = cacheNames
            .filter(cacheName => cacheName.startsWith(CACHE_PREFIX))
            .map(cacheName => {
                console.log('Deleting cache for auto-refresh:', cacheName);
                return caches.delete(cacheName);
            });
        
        await Promise.all(deletionPromises);
        console.log('Auto-refresh cache clear completed');
        
        // Notify all clients to refresh
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'CACHE_CLEARED',
                timestamp: Date.now()
            });
        });
        
        return true;
    } catch (error) {
        console.error('Error clearing caches:', error);
        return false;
    }
}

async function performAutoRefresh() {
    if (await shouldClearCache()) {
        console.log('24 hours passed - performing auto cache clear');
        await clearAllCaches();
        await setLastCacheClear(Date.now());
        return true;
    }
    return false;
}

// Install event - cache essential resources
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            caches.open(CACHE_NAME)
                .then((cache) => {
                    console.log('Caching static resources');
                    return cache.addAll(STATIC_CACHE_URLS);
                }),
            setLastCacheClear(Date.now()) // Set initial timestamp
        ]).then(() => {
            console.log('Initial cache setup completed');
            // Force the waiting service worker to become the active service worker
            return self.skipWaiting();
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches (except current and auto-refresh data)
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME && !cacheName.includes(LAST_CACHE_CLEAR_KEY)) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            // Check for auto-refresh
            performAutoRefresh()
        ]).then(() => {
            // Ensure the service worker takes control of all pages immediately
            return self.clients.claim();
        })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    // Perform periodic cache check (throttled to once per hour)
    periodicCacheCheck();
    
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Handle navigation requests
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.open(CACHE_NAME)
                        .then((cache) => {
                            return cache.match(OFFLINE_URL);
                        });
                })
        );
        return;
    }

    // Handle other requests with network-first strategy (minimum cache TTL)
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Always try network first for fresh content
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    throw new Error('Network response not ok');
                }

                // Check cache control headers for TTL
                const cacheControl = response.headers.get('cache-control');
                const shouldCache = !cacheControl || !cacheControl.includes('no-store');

                if (shouldCache) {
                    // Clone the response for caching
                    const responseToCache = response.clone();

                    // Cache with minimal TTL - remove old entries quickly
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                            
                            // Clean up old cached entries after 1 minute for minimum TTL
                            setTimeout(() => {
                                cache.delete(event.request);
                            }, 60 * 1000); // 1 minute
                        });
                }

                return response;
            })
            .catch(() => {
                // Network failed - fall back to cache as last resort
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            console.log('Using cached response for:', event.request.url);
                            return cachedResponse;
                        }
                        
                        // If it's a request for an HTML page, return the offline page
                        if (event.request.headers.get('accept') && 
                            event.request.headers.get('accept').includes('text/html')) {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // No cache available
                        throw new Error('No cached response available');
                    });
            })
    );
});

// Background sync (for future use)
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        console.log('Background sync triggered');
        // Implement background sync logic here
    }
});

// Push notifications (for future use)
self.addEventListener('push', (event) => {
    if (event.data) {
        const data = event.data.json();
        console.log('Push message received:', data);
        
        const options = {
            body: data.body,
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/icon-72x72.png',
            vibrate: [100, 50, 100],
            data: {
                dateOfArrival: Date.now(),
                primaryKey: data.primaryKey
            },
            actions: [
                {
                    action: 'explore',
                    title: 'View',
                    icon: '/static/icons/icon-192x192.png'
                },
                {
                    action: 'close',
                    title: 'Close',
                    icon: '/static/icons/icon-192x192.png'
                }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        // Open the app
                event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling for client communication
self.addEventListener('message', async (event) => {
    if (event.data && event.data.type === 'CHECK_CACHE_REFRESH') {
        console.log('Checking cache refresh status from client request');
        const refreshed = await performAutoRefresh();
        
        event.ports[0].postMessage({
            type: 'CACHE_REFRESH_RESULT',
            refreshed: refreshed,
            timestamp: Date.now()
        });
    }
});

// Periodic cache check during fetch events - aggressive checking
let lastCacheCheck = 0;
let lastCacheCleanup = 0;
const CACHE_CHECK_THROTTLE = 5 * 60 * 1000; // Check every 5 minutes (reduced from 1 hour)
const CACHE_CLEANUP_THROTTLE = 60 * 1000; // Cleanup every minute

async function cleanupStaleCache() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const requests = await cache.keys();
        
        const now = Date.now();
        let cleanedCount = 0;
        
        for (const request of requests) {
            // Remove entries that are part of old cache versions or have cache-busting params
            if (request.url.includes('_cache_ts=') || 
                request.url.includes('v=') || 
                request.url.includes('?t=')) {
                await cache.delete(request);
                cleanedCount++;
            }
        }
        
        if (cleanedCount > 0) {
            console.log(`Cleaned up ${cleanedCount} stale cache entries`);
        }
    } catch (error) {
        console.error('Error cleaning stale cache:', error);
    }
}

async function periodicCacheCheck() {
    const now = Date.now();
    
    // More frequent cache refresh checks
    if (now - lastCacheCheck > CACHE_CHECK_THROTTLE) {
        lastCacheCheck = now;
        console.log('Performing periodic cache check');
        await performAutoRefresh();
    }
    
    // Aggressive stale cache cleanup
    if (now - lastCacheCleanup > CACHE_CLEANUP_THROTTLE) {
        lastCacheCleanup = now;
        await cleanupStaleCache();
    }
}

// Message handling for client communication
self.addEventListener('message', async (event) => {
    if (event.data && event.data.type === 'CHECK_CACHE_REFRESH') {
        console.log('Checking cache refresh status from client request');
        const refreshed = await performAutoRefresh();
        
        event.ports[0].postMessage({
            type: 'CACHE_REFRESH_RESULT',
            refreshed: refreshed,
            timestamp: Date.now()
        });
    }
});

// Periodic cache check during fetch events - aggressive checking
let lastCacheCheck = 0;
let lastCacheCleanup = 0;
const CACHE_CHECK_THROTTLE = 5 * 60 * 1000; // Check every 5 minutes (reduced from 1 hour)
const CACHE_CLEANUP_THROTTLE = 60 * 1000; // Cleanup every minute

async function cleanupStaleCache() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const requests = await cache.keys();
        
        const now = Date.now();
        let cleanedCount = 0;
        
        for (const request of requests) {
            // Remove entries that are part of old cache versions
            if (request.url.includes('_cache_ts=') || 
                request.url.includes('v=') || 
                request.url.includes('?t=')) {
                await cache.delete(request);
                cleanedCount++;
            }
        }
        
        if (cleanedCount > 0) {
            console.log(`Cleaned up ${cleanedCount} stale cache entries`);
        }
    } catch (error) {
        console.error('Error cleaning stale cache:', error);
    }
}

async function periodicCacheCheck() {
    const now = Date.now();
    
    // More frequent cache refresh checks
    if (now - lastCacheCheck > CACHE_CHECK_THROTTLE) {
        lastCacheCheck = now;
        console.log('Performing periodic cache check');
        await performAutoRefresh();
    }
    
    // Aggressive stale cache cleanup
    if (now - lastCacheCleanup > CACHE_CLEANUP_THROTTLE) {
        lastCacheCleanup = now;
        await cleanupStaleCache();
    }
} 