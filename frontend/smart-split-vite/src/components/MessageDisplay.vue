<template>
  <div v-if="errorMessage || successMessage" class="mt-6 max-w-2xl mx-auto">
    <!-- Error Message -->
    <div v-if="errorMessage" class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl mb-4">
      <p class="text-red-600 dark:text-red-400 text-sm">{{ errorMessage }}</p>
    </div>
    
    <!-- Success Message -->
    <div v-if="successMessage" class="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
      <p class="text-green-600 dark:text-green-400 text-sm">{{ successMessage }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  errorMessage: string
  successMessage: string
}

defineProps<Props>();
</script>
