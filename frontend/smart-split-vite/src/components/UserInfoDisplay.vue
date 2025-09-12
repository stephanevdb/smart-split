<template>
  <div class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <h3 class="text-base font-semibold text-gray-800 dark:text-white mb-3">Account Info</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">Username:</span>
            <span class="text-gray-800 dark:text-white font-medium">{{ user?.username }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">Email:</span>
            <span class="text-gray-800 dark:text-white font-medium">{{ user?.email }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500 dark:text-gray-400">Member since:</span>
            <span class="text-gray-800 dark:text-white font-medium">{{ formatDate(user?.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type User } from '../services/api';

interface Props {
  user: User | null
}

defineProps<Props>();

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return 'Unknown';
  }
};
</script>
