<script setup lang="ts">
import Navbar from './components/Navbar.vue';
import ApiOfflineError from './components/ApiOfflineError.vue';
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
    <!-- API Offline Error - Full Screen Overlay -->
    <ApiOfflineError />
    
    <!-- Main Content Area -->
    <router-view />
    
    <!-- Navigation Bar -->
    <Navbar />
  </div>
</template>

