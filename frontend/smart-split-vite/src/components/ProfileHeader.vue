<template>
  <div class="text-center mb-8">
    <h1 class="text-4xl font-bold text-gray-800 dark:text-white mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
      Profile
    </h1>
    <p class="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
      {{ description }}
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  description: string
}

defineProps<Props>();
</script>
