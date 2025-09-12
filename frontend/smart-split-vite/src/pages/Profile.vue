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
          
          <!-- Google OAuth Section -->
          <div class="mb-6">
            <div class="text-center mb-3">
              <p class="text-gray-600 dark:text-gray-400 mb-3">Quick access with Google</p>
              <button
                @click="handleGoogleLogin"
                :disabled="isGoogleLoading"
                class="w-full max-w-sm mx-auto bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 font-semibold py-3 px-6 rounded-xl border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 flex items-center justify-center space-x-3"
              >
                <svg v-if="!isGoogleLoading" class="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <svg v-else class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>{{ isGoogleLoading ? 'Signing in...' : 'Continue with Google' }}</span>
              </button>
            </div>
            
            <div class="relative">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-2 bg-gray-50 dark:bg-gray-900 text-gray-500 dark:text-gray-400">Or continue with email</span>
              </div>
            </div>
          </div>
          
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
import { GOOGLE_CONFIG } from '../config/google';
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
const isGoogleLoading = ref(false); // New state for Google loading

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

// Google OAuth methods
const handleGoogleLogin = async () => {
  isGoogleLoading.value = true;
  try {
    console.log('Starting Google OAuth flow...');
    console.log('Current URL:', window.location.href);
    console.log('Client ID:', GOOGLE_CONFIG.CLIENT_ID);
    
    // Initialize Google Identity Services
    if (!(window as any).google) {
      console.log('Loading Google Identity Services script...');
      // Load Google Identity Services script
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
      
      await new Promise((resolve) => {
        script.onload = resolve;
      });
      console.log('Google Identity Services script loaded');
    }

    console.log('Initializing Google Sign-In client...');
    // Initialize Google Sign-In
    const client = (window as any).google.accounts.oauth2.initTokenClient({
      client_id: GOOGLE_CONFIG.CLIENT_ID,
      scope: GOOGLE_CONFIG.SCOPES,
      callback: async (response: { access_token?: string; error?: string }) => {
        try {
          if (response.error) {
            throw new Error(response.error);
          }
          
          if (!response.access_token) {
            throw new Error('No access token received from Google');
          }
          const authResponse = await apiService.googleLogin(response.access_token);
          handleAuthSuccess(authResponse.user);
        } catch (error) {
          errorMessage.value = error instanceof Error ? error.message : 'Failed to sign in with Google';
        } finally {
          isGoogleLoading.value = false;
        }
      }
    });

    client.requestAccessToken();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to initialize Google Sign-In';
    isGoogleLoading.value = false;
  }
};
</script>
