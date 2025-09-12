<template>
  <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
        Groups
      </h1>
      <p class="text-gray-600 dark:text-gray-300">
        Manage your expense splitting groups
      </p>
    </div>
    <div class="flex flex-row gap-2 mt-4 sm:mt-0">
      <button
        @click="$emit('join-group')"
        :disabled="!currentUser?.username"
        class="group relative bg-gradient-to-r from-green-600 to-emerald-600 text-white font-medium py-2 px-4 rounded-lg hover:from-green-700 hover:to-emerald-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-sm"
      >
        <div class="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        <div class="relative flex items-center space-x-1.5">
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
          </svg>
          <span>Join Group</span>
        </div>
      </button>
      
      <button
        @click="$emit('create-group')"
        :disabled="!currentUser?.username"
        class="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium py-2 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none text-sm"
      >
        <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
        <div class="relative flex items-center space-x-1.5">
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          <span>Create Group</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  currentUser?: any;
}

defineProps<Props>();

defineEmits<{
  'create-group': [];
  'join-group': [];
}>();
</script>
