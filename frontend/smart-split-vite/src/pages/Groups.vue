<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
    <div class="container mx-auto px-4 py-4">
      <!-- Main Content Area -->
      <main class="mt-4">
        <div class="p-4">
          <!-- Header Section -->
          <GroupsHeader 
            :current-user="currentUser" 
            @create-group="showCreateModal = true"
            @join-group="showJoinModal = true"
          />

          <!-- Loading State -->
          <div v-if="isLoading" class="text-center py-12">
            <div class="mx-auto w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
              <svg class="animate-spin w-12 h-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-2">Loading groups...</h3>
            <p class="text-gray-600 dark:text-gray-300">Please wait while we fetch your groups</p>
          </div>

          <!-- Error State -->
          <div v-else-if="errorMessage" class="text-center py-12">
            <div class="mx-auto w-24 h-24 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-6">
              <svg class="w-12 h-12 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-2">Error loading groups</h3>
            <p class="text-gray-600 dark:text-gray-300 mb-6">{{ errorMessage }}</p>
            <button
              @click="loadGroups"
              class="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              <div class="relative flex items-center space-x-2">
                <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                <span>Try Again</span>
              </div>
            </button>
          </div>

          <!-- Groups Grid -->
          <GroupsGrid 
            v-else-if="groups && groups.length > 0"
            :groups="groups"
            :current-user="currentUser"
            @view-group="viewGroup"
            @edit-group="editGroup"
            @delete-group="deleteGroup"
          />

          <!-- Empty State -->
          <GroupsEmptyState 
            v-else-if="!isLoading && !errorMessage"
            :current-user="currentUser"
            @create-group="showCreateModal = true"
          />
        </div>

        <!-- Create Group Modal -->
        <CreateGroupModal
          :show="showCreateModal"
          :is-creating="isCreating"
          :error-message="errorMessage"
          @close="showCreateModal = false; errorMessage = ''"
          @submit="createGroup"
        />
        
        <!-- Join Group Modal -->
        <JoinGroupModal
          :show="showJoinModal"
          :is-joining="isJoining"
          :error-message="joinErrorMessage"
          @close="showJoinModal = false; joinErrorMessage = ''"
          @submit="joinGroup"
        />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { apiService, type Group, type CreateGroupRequest } from '../services/api';
import GroupsHeader from '../components/GroupsHeader.vue';
import GroupsGrid from '../components/GroupsGrid.vue';
import GroupsEmptyState from '../components/GroupsEmptyState.vue';
import CreateGroupModal from '../components/CreateGroupModal.vue';
import JoinGroupModal from '../components/JoinGroupModal.vue';

const router = useRouter();

const groups = ref<Group[]>([]);
const showCreateModal = ref(false);
const showJoinModal = ref(false);
const isCreating = ref(false);
const isJoining = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const joinErrorMessage = ref('');

// Get current user from localStorage
const currentUser = computed(() => {
  const userStr = localStorage.getItem('currentUser');
  return userStr ? JSON.parse(userStr) : null;
});

onMounted(async () => {
  await loadGroups();
});

const loadGroups = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  if (!apiService.isAuthenticated()) {
    errorMessage.value = 'User not logged in';
    isLoading.value = false;
    return;
  }

  try {
    const response = await apiService.getGroups();
    groups.value = response.groups || [];
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load groups';
    console.error('Failed to load groups:', error);
    groups.value = []; // Ensure groups is always an array
  } finally {
    isLoading.value = false;
  }
};

const createGroup = async (newGroup: CreateGroupRequest) => {
  if (!apiService.isAuthenticated()) {
    errorMessage.value = 'User not logged in';
    return;
  }

  isCreating.value = true;
  errorMessage.value = '';
  
  try {
    const response = await apiService.createGroup(newGroup);
    if (!groups.value) {
      groups.value = [];
    }
    groups.value.unshift(response.group);
    
    showCreateModal.value = false;
    
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to create group';
    console.error('Failed to create group:', error);
  } finally {
    isCreating.value = false;
  }
};

const joinGroup = async (groupCode: string) => {
  if (!apiService.isAuthenticated()) {
    joinErrorMessage.value = 'User not logged in';
    return;
  }

  isJoining.value = true;
  joinErrorMessage.value = '';
  
  try {
    await apiService.joinGroup({ invite_code: groupCode });
    
    // Reload groups to show the newly joined group
    await loadGroups();
    
    showJoinModal.value = false;
    
  } catch (error) {
    joinErrorMessage.value = error instanceof Error ? error.message : 'Failed to join group';
    console.error('Failed to join group:', error);
  } finally {
    isJoining.value = false;
  }
};

const editGroup = (group: Group) => {
  // TODO: Implement edit functionality
  console.log('Edit group:', group);
};

const deleteGroup = async (groupId: string) => {
  if (!apiService.isAuthenticated()) {
    errorMessage.value = 'User not logged in';
    return;
  }

  if (!confirm('Are you sure you want to delete this group?')) {
    return;
  }

  try {
    await apiService.deleteGroup(groupId);
    if (groups.value) {
      groups.value = groups.value.filter(g => g.id !== groupId);
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to delete group';
    console.error('Failed to delete group:', error);
  }
};

const viewGroup = (group: Group) => {
  router.push(`/groups/${group.id}`);
};
</script>
