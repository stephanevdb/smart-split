<template>
  <div class="text-center py-12">
    <div class="mx-auto w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
      <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
    </div>
    <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-2">No groups yet</h3>
    <p class="text-gray-600 dark:text-gray-300 mb-6">Create your first group to start splitting expenses with friends</p>
    <button
      @click="$emit('create-group')"
      :disabled="!currentUser?.username"
      class="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
    >
      <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
      <div class="relative flex items-center space-x-2">
        <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Create Your First Group</span>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentUser?: any;
}

defineProps<Props>();

defineEmits<{
  'create-group': [];
}>();
</script>
