# Google Authentication Setup Guide for Manus Manager

This guide explains how to set up Google Authentication for your Manus Manager system.

## Prerequisites

1. A Google Cloud Platform account
2. Access to the Google Cloud Console
3. Manus Manager system installed and running

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a name for your project (e.g., "Manus Manager")
5. Click "Create"

## Step 2: Configure OAuth Consent Screen

1. In your Google Cloud project, go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you're using Google Workspace)
3. Click "Create"
4. Fill in the required information:
   - App name: "Manus Manager"
   - User support email: Your email address
   - Developer contact information: Your email address
5. Click "Save and Continue"
6. Add the following scopes:
   - `./auth/userinfo.email`
   - `./auth/userinfo.profile`
7. Click "Save and Continue"
8. Add test users if you're in testing mode
9. Click "Save and Continue"
10. Review your settings and click "Back to Dashboard"

## Step 3: Create OAuth 2.0 Client ID

1. In your Google Cloud project, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Web application" as the application type
4. Enter a name for your client (e.g., "Manus Manager Web Client")
5. Add authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - Your production domain (e.g., `https://your-manus-manager-domain.com`)
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (for development)
   - `https://your-manus-manager-domain.com/auth/google/callback` (for production)
7. Click "Create"
8. Note your Client ID and Client Secret

## Step 4: Configure Manus Manager

1. Open your `.env` file or environment configuration
2. Add the following environment variables:
   ```
   GOOGLE_CLIENT_ID=your_client_id_here
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
   ```
3. For the frontend, create a `.env` file in the frontend directory with:
   ```
   REACT_APP_GOOGLE_CLIENT_ID=your_client_id_here
   ```

## Step 5: Update Docker Compose Configuration

Ensure your `docker-compose.yml` file includes the Google authentication environment variables:

```yaml
services:
  backend:
    # ... other configuration ...
    environment:
      # ... other environment variables ...
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI}
```

## Step 6: Rebuild and Restart

1. Rebuild your Docker containers:
   ```bash
   docker-compose build
   ```
2. Restart your services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Testing Google Authentication

1. Open your Manus Manager application
2. Click on the "Sign in with Google" button on the login page
3. You should be redirected to Google's authentication page
4. After authenticating, you should be redirected back to your application and logged in

## Troubleshooting

### Common Issues

1. **Redirect URI mismatch**: Ensure the redirect URI in your Google Cloud Console matches exactly with the one in your application configuration.

2. **JavaScript origin not allowed**: Make sure your domain is listed in the authorized JavaScript origins in the Google Cloud Console.

3. **API not enabled**: You may need to enable the "Google+ API" or "People API" in your Google Cloud project.

4. **Consent screen not configured properly**: Ensure you've added the necessary scopes to your OAuth consent screen.

If you encounter any issues, check the browser console and server logs for specific error messages.
