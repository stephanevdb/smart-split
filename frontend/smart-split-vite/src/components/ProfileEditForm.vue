<template>
  <div class="max-w-2xl mx-auto mb-4">
    <h3 class="text-xl font-semibold text-gray-800 dark:text-white mb-6 text-center">Edit Profile</h3>
    <div class="space-y-6">
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
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            IBAN (Only used for EPC QR code payments)
          </label>
          <input
            v-model="form.iban"
            @input="handleIbanInput"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200 font-mono tracking-wider"
            placeholder="IBAN (optional)"
            maxlength="34"
          />
          <div v-if="ibanLoading" class="text-sm text-blue-600 mt-1">
            <svg class="animate-spin inline h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Fetching BIC...
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            BIC
          </label>
          <input
            v-model="form.bic"
            type="text"
            class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white transition-all duration-200 font-mono tracking-wider"
            placeholder="BIC (optional)"
          />
        </div>
      </div>
      <!-- Auto-save status indicator -->
      <div class="flex justify-center">
        <div v-if="autoSaveStatus !== 'idle'" class="flex items-center space-x-2 text-sm">
          <div v-if="autoSaveStatus === 'saving'" class="flex items-center text-blue-600 dark:text-blue-400">
            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Saving...
          </div>
          <div v-else-if="autoSaveStatus === 'saved'" class="flex items-center text-green-600 dark:text-green-400">
            <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Saved
          </div>
          <div v-else-if="autoSaveStatus === 'error'" class="flex items-center text-red-600 dark:text-red-400">
            <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            Save failed
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { type UpdateProfileRequest } from '../services/api';

interface Props {
  user: any
  isLoading: boolean
}

interface Emits {
  (e: 'update', profileData: UpdateProfileRequest): void
  (e: 'auto-save', profileData: UpdateProfileRequest): Promise<void>
}

interface OpenIBANResponse {
  valid: boolean
  messages: string[]
  iban: string
  bankData: {
    bankCode: string
    name: string
    zip: string
    city: string
    bic: string
  }
  checkResults: {
    bankCode: boolean
  }
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const form = reactive<UpdateProfileRequest>({
  full_name: '',
  iban: '',
  bic: ''
});

const ibanLoading = ref(false);
const autoSaveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle');
const autoSaveTimer = ref<number | null>(null);

// Function to fetch BIC from IBAN using OpenIBAN API
const fetchBICFromIBAN = async (iban: string) => {
  if (!iban || iban.length < 8) return;
  
  // Clear BIC if IBAN is too short
  if (iban.length < 8) {
    form.bic = '';
    return;
  }
  
  ibanLoading.value = true;
  
  try {
    const response = await fetch(`https://openiban.com/validate/${encodeURIComponent(iban)}?getBIC=true&validateBankCode=true`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data: OpenIBANResponse = await response.json();
    
    if (data.valid && data.bankData?.bic) {
      form.bic = data.bankData.bic;
    } else {
      // Clear BIC if IBAN is invalid or no BIC found
      form.bic = '';
    }
  } catch (error) {
    console.error('Error fetching BIC from IBAN:', error);
    // Don't clear BIC on error, let user keep what they have
  } finally {
    ibanLoading.value = false;
  }
};

// IBAN formatting functions
const formatIban = (iban: string): string => {
  // Remove all non-alphanumeric characters and convert to uppercase
  const cleaned = iban.replace(/[^A-Za-z0-9]/g, '').toUpperCase();
  
  // Group into chunks of 4 characters
  const chunks = [];
  for (let i = 0; i < cleaned.length; i += 4) {
    chunks.push(cleaned.slice(i, i + 4));
  }
  
  return chunks.join(' ');
};

const handleIbanInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const formatted = formatIban(target.value);
  form.iban = formatted;
};

// Debounced function to avoid too many API calls
let ibanDebounceTimer: number | null = null;
const debouncedFetchBIC = (iban: string) => {
  if (ibanDebounceTimer) {
    clearTimeout(ibanDebounceTimer);
  }
  
  ibanDebounceTimer = setTimeout(() => {
    fetchBICFromIBAN(iban);
  }, 1000); // Wait 1 second after user stops typing
};

// Watch for IBAN changes and fetch BIC
watch(() => form.iban, (newIban, oldIban) => {
  // Only fetch if IBAN actually changed and is not empty
  if (newIban !== oldIban && newIban) {
    // Remove spaces for BIC fetching
    const cleanedIban = newIban.replace(/\s/g, '');
    debouncedFetchBIC(cleanedIban);
  } else if (!newIban) {
    // Clear BIC if IBAN is empty
    form.bic = '';
  }
});

// Auto-save functionality
const autoSave = async () => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value);
  }
  
  autoSaveTimer.value = setTimeout(async () => {
    autoSaveStatus.value = 'saving';
    try {
      // Clean IBAN before sending to API (remove spaces)
      const cleanedForm = {
        ...form,
        iban: form.iban.replace(/\s/g, '')
      };
      await emit('auto-save', cleanedForm);
      autoSaveStatus.value = 'saved';
      // Hide success message after 2 seconds
      setTimeout(() => {
        autoSaveStatus.value = 'idle';
      }, 2000);
    } catch (error) {
      autoSaveStatus.value = 'error';
      // Hide error message after 3 seconds
      setTimeout(() => {
        autoSaveStatus.value = 'idle';
      }, 3000);
    }
  }, 1000); // Auto-save 1 second after user stops typing
};

// Watch for form changes and trigger auto-save
watch(() => form.full_name, () => {
  if (props.user) autoSave();
});

watch(() => form.iban, () => {
  if (props.user) autoSave();
});

watch(() => form.bic, () => {
  if (props.user) autoSave();
});

// Update form when user data changes
watch(() => props.user, (newUser) => {
  if (newUser) {
    form.full_name = newUser.full_name || '';
    form.iban = newUser.iban ? formatIban(newUser.iban) : '';
    form.bic = newUser.bic || '';
  }
}, { immediate: true });

const handleSubmit = () => {
  // Clean IBAN before sending to API (remove spaces)
  const cleanedForm = {
    ...form,
    iban: form.iban.replace(/\s/g, '')
  };
  emit('update', cleanedForm);
};
</script>
