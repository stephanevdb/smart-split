// Environment configuration for the frontend
export const config = {
  // Development environment - change this to your computer's IP when testing with phone
  development: {
    //apiBaseUrl: 'http://10.39.5.170:8145', // Your computer's IP address
    apiBaseUrl: 'http://localhost:8056' // Use nginx proxy for Docker development
  },
  
  // Production environment
  production: {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://v2.smartsplit.be'
  }
};

// Get current environment - check if we're in production build
const isProduction = import.meta.env.PROD;

// Export the appropriate configuration
export const currentConfig = isProduction ? config.production : config.development;

// Export API base URL for use in services
export const API_BASE_URL = currentConfig.apiBaseUrl;
