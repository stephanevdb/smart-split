<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-900 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl max-h-[90vh] overflow-y-auto relative">
      <!-- Close button -->
      <button
        @click="handleCancel"
        class="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 z-10"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
      
      <div class="text-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Create Account</h2>
        <p class="text-gray-600 dark:text-gray-300">Fill in your details to get started</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Username
            </label>
            <input
              v-model="form.username"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200"
              placeholder="Choose username"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Full Name
            </label>
            <input
              v-model="form.full_name"
              type="text"
              required
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200"
              placeholder="Your full name"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200"
            placeholder="your.email@example.com"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Password
          </label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200"
            placeholder="Create a password"
          />
          
          <!-- Password Strength Indicator -->
          <div v-if="form.password" class="mt-2">
            <div class="flex items-center space-x-2 mb-1">
              <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  class="h-2 rounded-full transition-all duration-300"
                  :class="passwordStrength.color"
                  :style="{ width: passwordStrength.width }"
                ></div>
              </div>
              <span class="text-xs font-medium" :class="passwordStrength.textColor">
                {{ passwordStrength.label }}
              </span>
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              <div v-if="passwordStrength.score < 3" class="space-y-1">
                <p>Password should include:</p>
                <ul class="list-disc list-inside space-y-0.5 ml-2">
                  <li :class="passwordChecks.length ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    At least 8 characters
                  </li>
                  <li :class="passwordChecks.uppercase ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    One uppercase letter
                  </li>
                  <li :class="passwordChecks.lowercase ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    One lowercase letter
                  </li>
                  <li :class="passwordChecks.number ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    One number
                  </li>
                  <li :class="passwordChecks.special ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    One special character
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Verify Password
          </label>
          <input
            v-model="form.verifyPassword"
            type="password"
            required
            class="w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200"
            :class="[
              form.verifyPassword && form.password
                ? form.password === form.verifyPassword
                  ? 'border-green-300 dark:border-green-600 bg-green-50 dark:bg-green-900/20'
                  : 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-300 dark:border-gray-600'
            ]"
            placeholder="Confirm your password"
          />
          <div v-if="form.verifyPassword && form.password" class="mt-1 text-sm">
            <span v-if="form.password === form.verifyPassword" class="text-green-600 dark:text-green-400 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Passwords match
            </span>
            <span v-else class="text-red-600 dark:text-red-400 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              Passwords do not match
            </span>
          </div>
        </div>
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full group relative bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
          <span v-if="isLoading" class="relative flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Creating Account...
          </span>
          <span v-else class="relative flex items-center justify-center space-x-2">
            <svg class="w-4 h-4 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
            </svg>
            <span>Create Account</span>
          </span>
        </button>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
        <p class="text-red-600 dark:text-red-400 text-sm">{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { apiService, type RegisterRequest } from '../services/api';

interface Props {
  isVisible: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'success', user: any): void
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isLoading = ref(false);
const errorMessage = ref('');

// Password strength calculation
const passwordChecks = computed(() => {
  const password = form.password;
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
  };
});

const passwordStrength = computed(() => {
  const password = form.password;
  if (!password) {
    return { score: 0, label: '', width: '0%', color: '', textColor: '' };
  }

  const checks = passwordChecks.value;
  let score = 0;
  
  // Calculate score based on criteria
  if (checks.length) score++;
  if (checks.uppercase) score++;
  if (checks.lowercase) score++;
  if (checks.number) score++;
  if (checks.special) score++;
  
  // Bonus for longer passwords
  if (password.length >= 12) score++;
  if (password.length >= 16) score++;

  const strengthLevels = [
    { score: 0, label: 'Very Weak', width: '20%', color: 'bg-red-500', textColor: 'text-red-600 dark:text-red-400' },
    { score: 1, label: 'Weak', width: '40%', color: 'bg-red-400', textColor: 'text-red-600 dark:text-red-400' },
    { score: 2, label: 'Fair', width: '60%', color: 'bg-yellow-500', textColor: 'text-yellow-600 dark:text-yellow-400' },
    { score: 3, label: 'Good', width: '80%', color: 'bg-blue-500', textColor: 'text-blue-600 dark:text-blue-400' },
    { score: 4, label: 'Strong', width: '90%', color: 'bg-green-500', textColor: 'text-green-600 dark:text-green-400' },
    { score: 5, label: 'Very Strong', width: '100%', color: 'bg-green-600', textColor: 'text-green-600 dark:text-green-400' }
  ];

  return strengthLevels[Math.min(score, 5)];
});

const form = reactive<RegisterRequest & { verifyPassword: string }>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  iban: '',
  bic: '',
  verifyPassword: ''
});

// Reset form when modal becomes visible
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    resetForm();
  }
});

const resetForm = () => {
  Object.assign(form, {
    username: '',
    email: '',
    password: '',
    full_name: '',
    iban: '',
    bic: '',
    verifyPassword: ''
  });
  errorMessage.value = '';
};

const handleSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  // Validate password match
  if (form.password !== form.verifyPassword) {
    errorMessage.value = 'Passwords do not match';
    isLoading.value = false;
    return;
  }

  // Validate password strength
  if (passwordStrength.value.score < 3) {
    errorMessage.value = 'Password is too weak. Please use a stronger password.';
    isLoading.value = false;
    return;
  }

  try {
    // Remove verifyPassword from the request data
    const { verifyPassword, ...registerData } = form;
    const response = await apiService.register(registerData);
    emit('success', response.user);
    resetForm();
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Registration failed';
  } finally {
    isLoading.value = false;
  }
};

const handleCancel = () => {
  resetForm();
  emit('close');
};
</script>
