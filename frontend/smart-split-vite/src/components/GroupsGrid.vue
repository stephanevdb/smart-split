<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div
      v-for="group in groups"
      :key="group.id"
      @click="$emit('view-group', group)"
      class="bg-white dark:bg-gray-900 rounded-2xl shadow-lg dark:shadow-gray-800/20 p-6 border border-gray-200 dark:border-gray-700 hover:shadow-xl dark:hover:shadow-gray-800/30 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-300 transform hover:scale-105 cursor-pointer"
    >
      <div class="flex justify-between items-start mb-4">
        <div class="flex-1">
          <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-1">
            {{ group.name }}
          </h3>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-2">
            {{ group.description || 'No description' }}
          </p>
        </div>
        <div class="flex space-x-2">
          <button
            v-if="currentUser?.id === group.created_by"
            @click.stop="$emit('delete-group', group.id)"
            class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            title="Delete Group (Creator only)"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Group } from '../services/api';

interface Props {
  groups: Group[];
  currentUser?: any;
}

defineProps<Props>();

defineEmits<{
  'view-group': [group: Group];
  'edit-group': [group: Group];
  'delete-group': [groupId: string];
}>();
</script>
