// Environment configuration for the frontend
export const config = {
  // Development environment - change this to your computer's IP when testing with phone
  development: {
    //apiBaseUrl: 'http://10.39.5.170:8145', // Your computer's IP address
    apiBaseUrl: 'http://localhost:8145' // Uncomment for local testing only
  },
  
  // Production environment
  production: {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8145'
  }
};

// Get current environment
const isDevelopment = import.meta.env.DEV;

// Export the appropriate configuration
export const currentConfig = isDevelopment ? config.development : config.production;

// Export API base URL for use in services
export const API_BASE_URL = currentConfig.apiBaseUrl;
