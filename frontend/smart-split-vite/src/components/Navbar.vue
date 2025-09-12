<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const navItems = [
  { icon: 'pi pi-home', label: 'Home', path: '/' },
  { icon: 'pi pi-users', label: 'Groups', path: '/groups' },
  { icon: 'pi pi-plus-circle', label: 'Add', path: '/add', isSpecial: true },
  { icon: 'pi pi-chart-bar', label: 'Activity', path: '/activity' },
  { icon: 'pi pi-user', label: 'Profile', path: '/profile' }
];

const isActive = (path: string) => route.path === path;

const navigateTo = (path: string) => {
  router.push(path);
};
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 shadow-lg">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <button 
          v-for="item in navItems" 
          :key="item.label"
          @click="navigateTo(item.path)"
          class="flex flex-col items-center justify-center flex-1 py-2 transition-all duration-200 relative"
          :class="[
            isActive(item.path)
              ? item.isSpecial 
                ? 'text-white' 
                : 'text-blue-600 dark:text-blue-400'
              : item.isSpecial
                ? 'text-white'
                : 'text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400'
          ]"
        >
          <!-- Special styling for Add button -->
          <div v-if="item.isSpecial" 
               class="absolute inset-0 mx-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg">
          </div>
          
          <div class="relative z-10 flex flex-col items-center">
            <i :class="[item.icon, 'text-xl mb-1', item.isSpecial ? 'text-2xl' : '']"></i>
            <span class="text-xs font-medium">{{ item.label }}</span>
          </div>
        </button>
      </div>
    </div>
  </nav>
</template>
