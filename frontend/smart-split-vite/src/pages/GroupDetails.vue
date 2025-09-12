<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation -->
    <Navbar />
    
    <div class="container mx-auto px-4 py-8">
      <!-- Loading State -->
      <LoadingSpinner
        v-if="isLoading"
        title="Loading group details..."
        description="Please wait while we fetch the group information"
      />

      <!-- Error State -->
      <ErrorState
        v-else-if="errorMessage"
        title="Error loading group"
        :message="errorMessage"
        @retry="loadGroupDetails"
        @go-back="$router.push('/groups')"
      />

      <!-- Group Details -->
      <div v-else-if="group" class="max-w-4xl mx-auto">
        <!-- Header -->
        <GroupHeader
          :group="group"
          :can-manage-group="currentUser?.id === group.created_by"
          @go-back="$router.push('/groups')"
          @edit-group="editGroup"
          @delete-group="deleteGroup"
          @copy-invite-code="copyInviteCode"
        />

        <!-- Members Section -->
        <GroupMembers
          :members="members"
          :is-loading="isLoadingMembers"
          :group-created-by="group.created_by"
          :can-remove-members="currentUser?.id === group.created_by"
          @remove-member="removeMember"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { apiService, type Group, type GroupMember } from '../services/api';
import Navbar from '../components/Navbar.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';
import ErrorState from '../components/ErrorState.vue';
import GroupHeader from '../components/GroupHeader.vue';
import GroupMembers from '../components/GroupMembers.vue';

const route = useRoute();
const router = useRouter();

const group = ref<Group | null>(null);
const members = ref<GroupMember[]>([]);
const isLoading = ref(false);
const isLoadingMembers = ref(false);
const errorMessage = ref('');

// Get current user from localStorage
const currentUser = computed(() => {
  const userStr = localStorage.getItem('currentUser');
  return userStr ? JSON.parse(userStr) : null;
});

onMounted(async () => {
  await loadGroupDetails();
});

const loadGroupDetails = async () => {
  const groupId = route.params.id as string;
  if (!groupId) {
    errorMessage.value = 'Group ID not provided';
    return;
  }

  if (!currentUser.value?.username) {
    errorMessage.value = 'User not logged in';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const response = await apiService.getGroup(groupId);
    group.value = response.group;
    await loadMembers();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load group details';
    console.error('Failed to load group details:', error);
  } finally {
    isLoading.value = false;
  }
};

const loadMembers = async () => {
  if (!group.value?.id || !currentUser.value?.username) return;

  isLoadingMembers.value = true;
  try {
    const response = await apiService.getGroup(group.value.id);
    members.value = response.members || [];
  } catch (error) {
    console.error('Failed to load members:', error);
    members.value = [];
  } finally {
    isLoadingMembers.value = false;
  }
};


const copyInviteCode = async () => {
  if (!group.value?.invite_code) return;
  
  try {
    await navigator.clipboard.writeText(group.value.invite_code);
    // TODO: Show success toast
    console.log('Invite code copied:', group.value.invite_code);
  } catch (error) {
    console.error('Failed to copy invite code:', error);
  }
};

const editGroup = () => {
  // TODO: Implement edit group functionality
  console.log('Edit group:', group.value);
};

const deleteGroup = async () => {
  if (!group.value?.id || !currentUser.value?.username) return;

  if (!confirm('Are you sure you want to delete this group? This action cannot be undone.')) {
    return;
  }

  try {
    await apiService.deleteGroup(group.value.id);
    router.push('/groups');
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to delete group';
    console.error('Failed to delete group:', error);
  }
};

const removeMember = async (userId: number) => {
  if (!group.value?.id || !currentUser.value?.username) return;

  if (!confirm('Are you sure you want to remove this member from the group?')) {
    return;
  }

  try {
    // TODO: Implement remove member API call
    console.log('Remove member:', userId);
    await loadMembers(); // Refresh members list
  } catch (error) {
    console.error('Failed to remove member:', error);
  }
};
</script>
