# Google OAuth Setup Guide

This guide will help you set up Google OAuth for the Smart Split application.

## Prerequisites

- A Google account
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Smart Split OAuth")
5. Click "Create"

## Step 2: Enable Required APIs

1. In your new project, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - Google+ API
   - Google Identity Services API

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen first:
   - User Type: External
   - App name: "Smart Split"
   - User support email: Your email
   - Developer contact information: Your email
   - Save and continue through the remaining steps

4. Back in Credentials, click "Create Credentials" > "OAuth 2.0 Client IDs"
5. Choose "Web application" as the application type
6. Name: "Smart Split Web Client"
7. Add these Authorized JavaScript origins:
   - `http://localhost:5173` (for development)
   - `http://localhost:3000` (alternative dev port)
   - Your production domain (when deployed)
8. Click "Create"
9. Copy the Client ID (you'll need this for the next step)

## Step 4: Update Application Configuration

1. Open `frontend/smart-split-vite/src/config/google.ts`
2. Replace `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID from step 3
3. Save the file

## Step 5: Test the Integration

1. Start your backend server: `cd backend && go run main.go`
2. Start your frontend: `cd frontend/smart-split-vite && npm run dev`
3. Navigate to the Profile page
4. Click "Continue with Google"
5. You should see the Google OAuth popup
6. Sign in with your Google account

## Troubleshooting

### Common Issues

1. **"Invalid Client ID" error**
   - Make sure you've updated the Client ID in `google.ts`
   - Verify the Client ID is correct in Google Cloud Console

2. **"Redirect URI mismatch" error**
   - Check that your domain is added to Authorized JavaScript origins
   - Make sure you're using the exact URL (including protocol and port)

3. **"API not enabled" error**
   - Ensure Google+ API and Google Identity Services are enabled
   - Wait a few minutes after enabling APIs

4. **CORS issues**
   - Verify your backend CORS settings include your frontend domain
   - Check that the Google OAuth endpoint is accessible

### Security Notes

- Never commit your actual Google Client ID to version control
- Consider using environment variables for production
- The current backend implementation is a demo - implement proper Google token verification for production
- Add rate limiting and proper error handling in production

## Production Considerations

1. **Token Verification**: Implement proper Google token verification using Google's userinfo endpoint
2. **User Management**: Implement proper user creation/linking logic
3. **Security**: Add CSRF protection and proper session management
4. **Error Handling**: Add comprehensive error handling and logging
5. **Rate Limiting**: Implement rate limiting for OAuth endpoints

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Identity Services](https://developers.google.com/identity/gsi/web)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
