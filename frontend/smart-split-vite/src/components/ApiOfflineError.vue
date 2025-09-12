<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { apiService } from '../services/api';

const isOffline = ref(false);
const lastCheckTime = ref<Date | null>(null);
const retryCount = ref(0);
const isRetrying = ref(false);
const networkStatus = ref<'online' | 'offline' | 'unknown'>('unknown');

let healthCheckInterval: number;

// Check if the browser thinks we're online
const checkBrowserNetworkStatus = () => {
  if ('onLine' in navigator) {
    networkStatus.value = navigator.onLine ? 'online' : 'offline';
    console.log('ApiOfflineError: Browser network status:', networkStatus.value);
  }
};


const checkApiHealth = async () => {
  console.log('ApiOfflineError: Checking API health...');
  try {
    isRetrying.value = true;
    await apiService.checkHealth();
    console.log('ApiOfflineError: API is online, hiding error');
    isOffline.value = false;
    lastCheckTime.value = new Date();
    retryCount.value = 0;
  } catch (error) {
    console.log('ApiOfflineError: API health check failed, showing offline error');
    isOffline.value = true;
    retryCount.value++;
  } finally {
    isRetrying.value = false;
  }
};

const manualRetry = async () => {
  console.log('ApiOfflineError: Manual retry requested');
  await checkApiHealth();
};

const formatLastCheck = (): string => {
  if (!lastCheckTime.value) return 'Never';
  return lastCheckTime.value.toLocaleTimeString();
};


// Listen for browser network status changes
const handleOnline = () => {
  console.log('ApiOfflineError: Browser went online');
  networkStatus.value = 'online';
  // Try to reconnect when browser comes back online
  if (isOffline.value) {
    checkApiHealth();
  }
};

const handleOffline = () => {
  console.log('ApiOfflineError: Browser went offline');
  networkStatus.value = 'offline';
  isOffline.value = true;
};

onMounted(() => {
  console.log('ApiOfflineError: Component mounted, starting health checks');
  
  // Check browser network status first
  checkBrowserNetworkStatus();
  
  // Initial API health check
  checkApiHealth();
  
  // Set up periodic checks - only check when we think we're offline
  healthCheckInterval = setInterval(() => {
    // Only perform periodic checks if we're currently showing the offline error
    // This prevents unnecessary API calls when the service is working
    if (isOffline.value) {
      checkApiHealth();
    }
  }, 10000); // Check every 10 seconds when offline
  
  // Listen for browser network status changes
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
});

onUnmounted(() => {
  if (healthCheckInterval) {
    clearInterval(healthCheckInterval);
  }
  window.removeEventListener('online', handleOnline);
  window.removeEventListener('offline', handleOffline);
});
</script>

<template>
  <div v-if="isOffline" class="fixed inset-0 bg-red-50 dark:bg-red-900/20 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border-2 border-red-200 dark:border-red-800 p-8 max-w-lg w-full text-center">
      <!-- Connection Status Icon -->
      <div class="mx-auto w-20 h-20 bg-red-100 dark:bg-red-900/50 rounded-full flex items-center justify-center mb-6">
        <svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"></path>
        </svg>
      </div>

      <!-- Friendly Title -->
      <h1 class="text-2xl font-bold text-red-800 dark:text-red-200 mb-3">
        Connection Issue Detected
      </h1>

      <!-- Encouraging Message -->
      <p class="text-red-600 dark:text-red-300 mb-6 leading-relaxed">
        We're having trouble reaching our servers due to a network connectivity issue. This error only appears when we can't establish a connection to our API - not when the API returns error responses.
      </p>

      <!-- What You Can Do Section -->
      <div class="bg-blue-50 dark:bg-blue-900/30 rounded-xl p-4 mb-6 text-left border border-blue-200 dark:border-blue-800">
        <h3 class="font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          What you can try:
        </h3>
        <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-2">
          <li class="flex items-start">
            <span class="text-blue-500 mr-2">•</span>
            Check your internet connection
          </li>
          <li class="flex items-start">
            <span class="text-blue-500 mr-2">•</span>
            Check if your network allows connections to our API server
          </li>
          <li class="flex items-start">
            <span class="text-blue-500 mr-2">•</span>
            Try refreshing the page or restarting your browser
          </li>
          <li class="flex items-start">
            <span class="text-blue-500 mr-2">•</span>
            If the problem persists, it may be a server-side network issue
          </li>
        </ul>
      </div>

      <!-- Connection Status -->
      <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 mb-6">
        <div class="flex items-center justify-center mb-3">
          <div class="w-3 h-3 bg-red-500 rounded-full mr-2 animate-pulse"></div>
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Attempting to reconnect...</span>
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400">
          Last checked: {{ formatLastCheck() }} • Auto-retry: {{ retryCount }} attempts
        </div>
        <!-- Network Status -->
        <div class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-center">
            <div class="w-2 h-2 rounded-full mr-2" :class="{
              'bg-green-500': networkStatus === 'online',
              'bg-red-500': networkStatus === 'offline',
              'bg-yellow-500': networkStatus === 'unknown'
            }"></div>
            <span class="text-xs text-gray-600 dark:text-gray-400">
              Browser network: {{ networkStatus === 'online' ? 'Online' : networkStatus === 'offline' ? 'Offline' : 'Unknown' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="space-y-3">
        <button
          @click="manualRetry"
          :disabled="isRetrying"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-xl transition-colors duration-200 flex items-center justify-center"
        >
          <svg v-if="isRetrying" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isRetrying ? 'Trying to connect...' : 'Try Again Now' }}
        </button>
      </div>

      <!-- Reassuring Message -->
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-4">
        We'll keep trying to reconnect automatically. Your data is safe and will sync once we're back online.
      </p>
    </div>
  </div>
</template>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
