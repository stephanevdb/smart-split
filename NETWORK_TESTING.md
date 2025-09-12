# Network Testing Guide

This guide explains how to test the Smart Split application with your phone on the same local network.

## Prerequisites

1. **Both devices must be on the same WiFi network**
2. **Your computer's firewall must allow incoming connections on port 8145**
3. **Your Go backend must be running**

## Step 1: Find Your Computer's IP Address

### On macOS/Linux:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### On Windows:
```cmd
ipconfig | findstr "IPv4"
```

Look for an IP address like `10.39.5.170` (your computer's local IP).

## Step 2: Update Configuration

### Backend Configuration
The backend is already configured to bind to `0.0.0.0:8145` which allows external connections.

### Frontend Configuration
Edit `frontend/smart-split-vite/src/config/environment.ts`:

```typescript
development: {
  apiBaseUrl: 'http://YOUR_COMPUTER_IP:8145', // Replace with your actual IP
  // apiBaseUrl: 'http://localhost:8145', // Comment this out
},
```

## Step 3: Start the Backend

```bash
cd backend
go run .
```

You should see: `Starting server on 0.0.0.0:8145`

## Step 4: Start the Frontend

```bash
cd frontend/smart-split-vite
npm run dev -- --host 0.0.0.0
```

The `--host 0.0.0.0` flag makes Vite accessible from other devices.

## Step 5: Test on Your Phone

1. **Open your phone's browser**
2. **Navigate to**: `http://YOUR_COMPUTER_IP:5173`
3. **Test the application**

## Troubleshooting

### "Connection Refused" Error
- Check if your computer's firewall is blocking port 8145
- Ensure the backend is running
- Verify the IP address is correct

### CORS Errors
- The backend is configured to accept connections from your network IP
- Check the browser console for CORS-related errors

### Network Unreachable
- Ensure both devices are on the same WiFi network
- Try pinging your computer from your phone to test connectivity

## Security Note

⚠️ **Warning**: Binding to `0.0.0.0` makes your server accessible to anyone on your local network. This is fine for development but should not be used in production.

## Environment Variables

You can also use environment variables to configure the backend:

```bash
export SERVER_HOST=0.0.0.0
export SERVER_PORT=8145
export ALLOWED_CORS_ORIGINS=http://YOUR_PHONE_IP:5173
go run .
```

## Quick Test Commands

Test if your backend is accessible:
```bash
curl http://YOUR_COMPUTER_IP:8145/api/health
```

Test if your frontend is accessible:
```bash
curl http://YOUR_COMPUTER_IP:5173
```
