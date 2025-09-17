<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-300">
    <div class="container mx-auto px-4 py-4">
      <!-- Main Content Area -->
      <main class="mt-4">
        <!-- Login/Signup Options (when not logged in) -->
        <div v-if="!isLoggedIn" class="p-4">
          <ProfileHeader 
            description="Please sign in to your account or create a new one to view and manage your profile settings."
          />
          
          
          <div class="flex flex-col sm:flex-row justify-center gap-3">
            <button
              @click="showLoginForm = true"
              class="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg overflow-hidden"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              <div class="relative flex items-center justify-center space-x-2">
                <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
                </svg>
                <span>Sign In</span>
              </div>
            </button>
            <button
              @click="showSignupForm = true"
              class="group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-300 transform hover:scale-105 hover:shadow-xl shadow-lg overflow-hidden"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              <div class="relative flex items-center justify-center space-x-2">
                <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                </svg>
                <span>Sign Up</span>
              </div>
            </button>
          </div>

          <!-- Login Modal -->
          <LoginModal
            :is-visible="showLoginForm"
            @close="showLoginForm = false"
            @success="handleAuthSuccess"
          />

          <!-- Sign Up Modal -->
          <SignupModal
            :is-visible="showSignupForm"
            @close="showSignupForm = false"
            @success="handleAuthSuccess"
          />
        </div>

        <!-- Profile Management Section (when logged in) -->
        <div v-if="isLoggedIn" class="p-4">
          <ProfileHeader 
            description="Manage your account settings and personal information."
          />

          <!-- User Info Display -->
          <UserInfoDisplay :user="currentUser" />

          <!-- Edit Profile Form -->
          <ProfileEditForm
            :user="currentUser"
            :is-loading="isLoading"
            @update="handleUpdateProfile"
            @auto-save="handleAutoSave"
          />

          <!-- Success/Error Messages -->
          <MessageDisplay
            :error-message="errorMessage"
            :success-message="successMessage"
          />

          <!-- Sign Out Button at Bottom -->
          <div class="text-center mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="handleLogout"
              class="bg-gray-500 text-white font-semibold py-3 px-8 rounded-xl hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 transform hover:scale-105"
            >
              Sign Out
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { apiService, type User, type UpdateProfileRequest } from '../services/api';
import LoginModal from '../components/LoginModal.vue';
import SignupModal from '../components/SignupModal.vue';
import ProfileHeader from '../components/ProfileHeader.vue';
import UserInfoDisplay from '../components/UserInfoDisplay.vue';
import ProfileEditForm from '../components/ProfileEditForm.vue';
import MessageDisplay from '../components/MessageDisplay.vue';

// State
const isLoggedIn = ref(false);
const currentUser = ref<User | null>(null);
const showLoginForm = ref(false);
const showSignupForm = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// Check if user is logged in on component mount
onMounted(() => {
  const savedUser = localStorage.getItem('currentUser');
  if (savedUser) {
    try {
      currentUser.value = JSON.parse(savedUser);
      isLoggedIn.value = true;
    } catch (error) {
      console.error('Error parsing saved user:', error);
      localStorage.removeItem('currentUser');
    }
  }
});

// Methods
const handleAuthSuccess = (user: User) => {
  currentUser.value = user;
  isLoggedIn.value = true;
  
  // Save user to localStorage
  localStorage.setItem('currentUser', JSON.stringify(user));
  
  // Close modals
  showLoginForm.value = false;
  showSignupForm.value = false;
  
  // Show success message
  successMessage.value = 'Successfully authenticated!';
  
  // Clear success message after 3 seconds
  setTimeout(() => {
    successMessage.value = '';
  }, 3000);
};

const handleUpdateProfile = async (profileData: UpdateProfileRequest) => {
  if (!currentUser.value) return;
  
  isLoading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    const response = await apiService.updateProfile(profileData);
    currentUser.value = response.user;
    
    // Update localStorage
    localStorage.setItem('currentUser', JSON.stringify(response.user));
    
    successMessage.value = 'Profile updated successfully!';
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to update profile';
  } finally {
    isLoading.value = false;
  }
};

const handleAutoSave = async (profileData: UpdateProfileRequest) => {
  if (!currentUser.value?.username) {
    console.error('No username available for auto-save');
    return;
  }
  
  try {
    await apiService.updateProfile(profileData);
    // Update local user data
    if (currentUser.value) {
      currentUser.value = { ...currentUser.value, ...profileData };
      localStorage.setItem('currentUser', JSON.stringify(currentUser.value));
    }
    // Auto-save success will be handled by the component's status indicator
  } catch (error) {
    // Auto-save error will be handled by the component's status indicator
    console.error('Auto-save failed:', error);
  }
};

const handleLogout = () => {
  currentUser.value = null;
  isLoggedIn.value = false;
  localStorage.removeItem('currentUser');
  
  // Clear messages
  errorMessage.value = '';
  successMessage.value = '';
};
</script>
