<template>
  <div v-if="show" class="fixed inset-0 backdrop-blur-md flex items-center justify-center z-50 p-4">
    <div class="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl w-full max-w-md transform transition-all duration-300 scale-100 animate-in fade-in-0 zoom-in-95">
      <!-- Header with icon -->
      <div class="flex items-center justify-between p-8 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-3xl font-bold text-gray-800 dark:text-white">Join Group</h2>
            <p class="text-gray-600 dark:text-gray-300 text-sm">Enter the group code to join</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="p-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-all duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 hover:scale-110"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-8">
        <form @submit.prevent="handleSubmit" class="space-y-8">
          <div class="space-y-3">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4 flex items-center">
              <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
              </svg>
              Group Code
            </label>
            <input
              v-model="groupCode"
              type="text"
              required
              class="w-full px-6 py-5 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:ring-4 focus:ring-green-500/20 focus:border-green-500 dark:bg-gray-700 dark:text-white transition-all duration-300 font-mono tracking-wider text-lg text-center placeholder-gray-400 dark:placeholder-gray-500 hover:border-gray-300 dark:hover:border-gray-600"
              placeholder="Enter group code"
              :disabled="isJoining"
            />
            <div class="flex items-center justify-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mt-3">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Ask the group creator for the group code to join</span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-2xl p-4 animate-in slide-in-from-top-2 duration-300">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <p class="text-sm text-red-600 dark:text-red-400 font-medium">{{ errorMessage }}</p>
            </div>
          </div>

          <!-- Join Button -->
          <div class="pt-2">
            <button
              type="submit"
              :disabled="isJoining || !groupCode.trim()"
              class="w-full px-8 py-5 bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 text-white font-bold rounded-2xl hover:from-green-700 hover:via-emerald-700 hover:to-teal-700 focus:outline-none focus:ring-4 focus:ring-green-500/30 focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transform hover:scale-105 hover:shadow-2xl shadow-lg"
            >
              <div v-if="isJoining" class="flex items-center justify-center text-xl">
                <svg class="animate-spin w-7 h-7 mr-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Joining Group...
              </div>
              <span v-else class="flex items-center justify-center space-x-3 text-xl">
                <svg class="w-6 h-6 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                <span>Join Group</span>
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  show: boolean;
  isJoining: boolean;
  errorMessage: string;
}

interface Emits {
  (e: 'close'): void;
  (e: 'submit', groupCode: string): void;
}

defineProps<Props>();
const emit = defineEmits<Emits>();

const groupCode = ref('');

const handleSubmit = () => {
  if (groupCode.value.trim()) {
    emit('submit', groupCode.value.trim());
  }
};
</script>
