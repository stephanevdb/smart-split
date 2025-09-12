// Google OAuth Configuration
export const GOOGLE_CONFIG = {
  CLIENT_ID: '800785828190-efeom1ec5a8onpto5hqhkc4saafkcml9.apps.googleusercontent.com', // Replace with your actual Google Client ID from Google Cloud Console
  
  // Scopes for OAuth
  SCOPES: 'openid email profile',
  
  // Google Identity Services script URL
  SCRIPT_URL: 'https://accounts.google.com/gsi/client'
};

// Instructions to get your Google Client ID:
// 1. Go to https://console.cloud.google.com/
// 2. Create a new project or select existing one
// 3. Enable Google+ API and Google Identity Services
// 4. Go to Credentials > Create Credentials > OAuth 2.0 Client IDs
// 5. Set Application Type to "Web application"
// 6. Add your domain to Authorized JavaScript origins (e.g., http://localhost:5173)
// 7. Copy the Client ID and replace 'YOUR_GOOGLE_CLIENT_ID' above
