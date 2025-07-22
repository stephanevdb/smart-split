// PWA App JavaScript

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('Service Worker registered successfully:', registration.scope);
                
                // Set up auto-refresh listeners
                setupAutoRefresh(registration);
                
                // Check for updates periodically
                setInterval(() => {
                    registration.update();
                }, 60000); // Check every minute
            })
            .catch((error) => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// Auto-refresh functionality
function setupAutoRefresh(registration) {
    // Listen for messages from service worker
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'CACHE_CLEARED') {
            console.log('Cache cleared automatically - refreshing page');
            showNotification('App updated! Refreshing...', 'info');
            
            // Refresh the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    });
    
    // Manual cache refresh function (can be called from UI)
    window.refreshAppCache = async () => {
        try {
            const messageChannel = new MessageChannel();
            
            return new Promise((resolve) => {
                messageChannel.port1.onmessage = (event) => {
                    if (event.data && event.data.type === 'CACHE_REFRESH_RESULT') {
                        if (event.data.refreshed) {
                            showNotification('Cache cleared successfully!', 'success');
                            setTimeout(() => {
                                window.location.reload();
                            }, 1500);
                        } else {
                            showNotification('Cache is still fresh', 'info');
                        }
                        resolve(event.data.refreshed);
                    }
                };
                
                // Send message to service worker
                if (registration.active) {
                    registration.active.postMessage(
                        { type: 'CHECK_CACHE_REFRESH' },
                        [messageChannel.port2]
                    );
                }
            });
        } catch (error) {
            console.error('Error refreshing cache:', error);
            showNotification('Error refreshing cache', 'error');
        }
    };
    
    // Check cache status on page load
    setTimeout(() => {
        if (window.refreshAppCache) {
            console.log('Checking cache status on startup...');
            window.refreshAppCache();
        }
    }, 5000); // Wait 5 seconds after page load
}

// Install Prompt
let deferredPrompt;
const installPrompt = document.getElementById('installPrompt');
const installBtn = document.getElementById('installBtn');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent the mini-infobar from appearing on mobile
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show the install button
    if (installPrompt) {
        installPrompt.style.display = 'block';
    }
});

if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (deferredPrompt) {
            // Show the install prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            // Clear the deferredPrompt variable
            deferredPrompt = null;
            // Hide the install button
            installPrompt.style.display = 'none';
        }
    });
}

// Handle app installed event
window.addEventListener('appinstalled', (evt) => {
    console.log('PWA was installed');
    // Hide the install button
    if (installPrompt) {
        installPrompt.style.display = 'none';
    }
});

// Online/Offline Detection
window.addEventListener('online', () => {
    console.log('Back online');
    showNotification('You are back online!', 'success');
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    showNotification('You are offline. Some features may not work.', 'warning');
});

// Notification Function
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 5px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#27ae60';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f39c12';
            break;
        case 'error':
            notification.style.backgroundColor = '#e74c3c';
            break;
        default:
            notification.style.backgroundColor = '#2196F3';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add some PWA debugging info to console
console.log('PWA initialized');
console.log('Service Worker supported:', 'serviceWorker' in navigator);
console.log('Currently online:', navigator.onLine);

// Debug: Add global function for testing cache refresh
if (typeof window !== 'undefined') {
    window.testCacheRefresh = () => {
        console.log('Testing cache refresh functionality...');
        if (window.refreshAppCache) {
            window.refreshAppCache();
        } else {
            console.log('Cache refresh not yet available - try again in a few seconds');
        }
    };
    
    console.log('🔧 Debug: Type "testCacheRefresh()" in console to test cache refresh');
}

// Theme color detection
function updateThemeColor() {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const themeColor = isDark ? '#1565C0' : '#2196F3';
    
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.setAttribute('content', themeColor);
    }
}

// Update theme color on load and when system theme changes
updateThemeColor();
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateThemeColor);

// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navContainer = document.getElementById('navContainer');
    const navLinks = document.querySelectorAll('.nav-link');

    if (mobileMenuToggle && navContainer) {
        // Toggle mobile menu
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navContainer.classList.toggle('active');
            
            // Prevent body scrolling when menu is open
            if (navContainer.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking on a nav link
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                navContainer.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close menu when clicking outside (on mobile overlay)
        navContainer.addEventListener('click', function(e) {
            if (e.target === navContainer) {
                mobileMenuToggle.classList.remove('active');
                navContainer.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navContainer.classList.contains('active')) {
                mobileMenuToggle.classList.remove('active');
                navContainer.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                mobileMenuToggle.classList.remove('active');
                navContainer.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
}); 