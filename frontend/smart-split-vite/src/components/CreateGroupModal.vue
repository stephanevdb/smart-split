<template>
  <div v-if="props.show" class="fixed inset-0 backdrop-blur-md flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-900 rounded-3xl p-8 max-w-md w-full shadow-2xl relative transform transition-all duration-300 scale-100 animate-in fade-in-0 zoom-in-95">
      <!-- Close button -->
      <button
        @click="emit('close')"
        class="absolute top-6 right-6 p-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-all duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-110"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
      
      <!-- Header with icon -->
      <div class="text-center mb-8">
        <div class="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-800 dark:text-white mb-2">Create New Group</h2>
        <p class="text-gray-600 dark:text-gray-300 text-lg">Set up a new expense splitting group</p>
      </div>
      
      <form @submit.prevent="emit('submit', newGroup)" class="space-y-6">
        <div class="space-y-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
            </svg>
            Group Name
          </label>
          <input
            v-model="newGroup.name"
            type="text"
            required
            class="w-full px-4 py-4 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:bg-gray-800 dark:text-white transition-all duration-300 text-lg placeholder-gray-400 dark:placeholder-gray-500 hover:border-gray-300 dark:hover:border-gray-600"
            placeholder="Enter group name"
          />
        </div>
        <div class="space-y-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Description (Optional)
          </label>
          <textarea
            v-model="newGroup.description"
            rows="3"
            class="w-full px-4 py-4 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 dark:bg-gray-800 dark:text-white transition-all duration-300 text-lg placeholder-gray-400 dark:placeholder-gray-500 hover:border-gray-300 dark:hover:border-gray-600 resize-none"
            placeholder="Describe your group"
          ></textarea>
        </div>
        <button
          type="submit"
          :disabled="props.isCreating"
          class="w-full group relative bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white font-bold py-4 px-8 rounded-2xl hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 focus:outline-none focus:ring-4 focus:ring-blue-500/30 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 hover:shadow-2xl overflow-hidden shadow-lg"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
          <div class="absolute inset-0 bg-white opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
          <span v-if="props.isCreating" class="relative flex items-center justify-center text-lg">
            <svg class="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Creating Group...
          </span>
          <span v-else class="relative flex items-center justify-center space-x-3 text-lg">
            <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110 group-hover:rotate-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            <span>Create Group</span>
          </span>
        </button>
      </form>

      <!-- Error Message in Modal -->
      <div v-if="props.errorMessage" class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-2xl animate-in slide-in-from-top-2 duration-300">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p class="text-red-600 dark:text-red-400 text-sm font-medium">{{ props.errorMessage }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import type { CreateGroupRequest } from '../services/api';

interface Props {
  show: boolean;
  isCreating: boolean;
  errorMessage: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  submit: [group: CreateGroupRequest];
}>();

const newGroup = reactive<CreateGroupRequest>({
  name: '',
  description: ''
});

// Reset form when modal closes
watch(() => props.show, (newValue) => {
  if (!newValue) {
    newGroup.name = '';
    newGroup.description = '';
  }
});
</script>
