<template>
  <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-lg dark:shadow-gray-800/20 p-8 border border-gray-200 dark:border-gray-700">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-6">Members</h2>
    
    <!-- Loading Members -->
    <LoadingSpinner
      v-if="isLoading"
      title="Loading members..."
      description=""
    />

    <!-- Members List -->
    <div v-else-if="members && members.length > 0" class="space-y-4">
      <div
        v-for="member in members"
        :key="member.id"
        class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
      >
        <div class="flex items-center space-x-4">
          <div class="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
            {{ member.user?.username ? member.user.username.charAt(0).toUpperCase() : '?' }}
          </div>
          <div>
            <h3 class="font-medium text-gray-800 dark:text-white">{{ member.user?.username || 'Unknown User' }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Joined {{ formatDate(member.joined_at) }}</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <span v-if="member.user_id === groupCreatedBy" class="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 text-xs font-medium rounded-full">
            Creator
          </span>
          <button
            v-if="member.user_id !== groupCreatedBy && canRemoveMembers"
            @click="$emit('removeMember', member.user_id)"
            class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            title="Remove Member"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- No Members -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-800 dark:text-white mb-2">No members yet</h3>
      <p class="text-gray-600 dark:text-gray-300">Share the invite code to add members to this group</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GroupMember } from '../services/api';
import LoadingSpinner from './LoadingSpinner.vue';

interface Props {
  members: GroupMember[];
  isLoading: boolean;
  groupCreatedBy: number;
  canRemoveMembers: boolean;
}

defineProps<Props>();

defineEmits<{
  removeMember: [userId: number];
}>();

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};
</script>
