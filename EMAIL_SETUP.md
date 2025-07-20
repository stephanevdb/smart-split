# 📧 Email Setup for Password Reset

Smart Split now includes password reset functionality with email verification. This guide will help you set up email sending capabilities.

## 🚀 Quick Setup

### 1. Create Environment File

Create a `.env` file in your project root with the following configuration:

```env
# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-change-in-production
DATABASE=splitwise.db

# AI Receipt Scanning (Optional)
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration for Password Reset
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 2. Choose Your Email Provider

## 📧 Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Follow the setup process to enable 2FA

### Step 2: Generate App Password
1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select **Mail** as the app
3. Select **Other** as the device and enter "Smart Split"
4. Copy the generated 16-character password
5. Use this password for `MAIL_PASSWORD` (not your regular Gmail password)

### Step 3: Update Environment Variables
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## 📨 Other Email Providers

### Outlook/Hotmail
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@outlook.com
```

### Yahoo Mail
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@yahoo.com
```

### Custom SMTP Server
```env
MAIL_SERVER=mail.yourdomain.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=your-smtp-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

## 🔧 Docker Configuration

### Option 1: Environment File (Recommended)
Create a `.env` file in your project directory with the email settings above.

### Option 2: Docker Compose Override
Create a `docker-compose.override.yml` file:

```yaml
version: '3.8'
services:
  smart-split:
    environment:
      - MAIL_SERVER=smtp.gmail.com
      - MAIL_PORT=587
      - MAIL_USE_TLS=True
      - MAIL_USERNAME=your-email@gmail.com
      - MAIL_PASSWORD=your-app-password
      - MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### Option 3: Direct Environment Variables
```bash
export MAIL_SERVER=smtp.gmail.com
export MAIL_PORT=587
export MAIL_USE_TLS=True
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
export MAIL_DEFAULT_SENDER=your-email@gmail.com

docker-compose up -d
```

## 🧪 Testing Email Functionality

### 1. Start the Application
```bash
# Local development
python app.py

# Docker
docker-compose up
```

### 2. Test Password Reset
1. Navigate to the login page
2. Click "🔐 Forgot your password?"
3. Enter a valid email address
4. Check your inbox for the reset email

### 3. Verify Email Content
The reset email should include:
- ✅ Branded header with Smart Split logo
- ✅ Clear reset instructions
- ✅ Clickable reset button
- ✅ Security warnings (1-hour expiration, one-time use)
- ✅ Support contact information

## 🛠️ Troubleshooting

### Common Issues

#### "Failed to send reset email"
- **Check credentials**: Verify `MAIL_USERNAME` and `MAIL_PASSWORD`
- **Check 2FA**: Ensure you're using an app password, not your regular password
- **Check network**: Ensure your server can access the SMTP server
- **Check spam**: Look in the spam/junk folder

#### "The message does not specify a sender and a default sender has not been configured"
- **Set MAIL_DEFAULT_SENDER**: Ensure this environment variable is set
- **Alternative**: Set MAIL_USERNAME (will be used as fallback sender)
- **Docker users**: Make sure environment variables are properly passed to the container
- **Example fix**: 
  ```env
  MAIL_DEFAULT_SENDER=noreply@yourdomain.com
  MAIL_USERNAME=your-email@gmail.com
  ```

#### "Authentication failed"
- **Gmail**: Ensure 2FA is enabled and you're using an app password
- **Outlook**: May need to enable "Less secure app access"
- **Yahoo**: Use an app password instead of your regular password

#### "Connection timeout"
- **Firewall**: Check if port 587 (or 465 for SSL) is blocked
- **TLS/SSL**: Try toggling `MAIL_USE_TLS` and `MAIL_USE_SSL` settings
- **Port**: Try alternative ports (25, 465, 2525)

### Debug Mode
Add this to your environment for detailed email debugging:
```env
FLASK_ENV=development
MAIL_DEBUG=True
```

### Check Email Configuration
Visit the debug endpoint to verify your email configuration:
```
http://localhost:3000/debug/email-config
```

This endpoint (available only in development mode) will show:
- ✅ Current email configuration settings
- ✅ Whether a sender is properly configured
- ✅ Whether the setup is ready to send emails

Example response:
```json
{
  "email_config": {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": true,
    "MAIL_USERNAME": "your-email@gmail.com",
    "MAIL_DEFAULT_SENDER": "your-email@gmail.com",
    "MAIL_PASSWORD_SET": true
  },
  "sender_available": true,
  "ready_to_send": true
}
```

### Testing Without Email
For development, you can use [MailHog](https://github.com/mailhog/MailHog) to catch emails locally:

```bash
# Install MailHog
brew install mailhog  # macOS
# or download from GitHub releases

# Run MailHog
mailhog

# Configure Smart Split to use MailHog
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
```

Then visit http://localhost:8025 to see caught emails.

## 🔒 Security Best Practices

### Production Deployment
1. **Use app passwords**: Never use your main email password
2. **Dedicated email**: Consider using a dedicated email account for the app
3. **Rate limiting**: The app includes basic rate limiting for password resets
4. **HTTPS required**: Email links will only work with HTTPS in production
5. **Monitor logs**: Keep an eye on email sending logs

### Email Security
- **SPF records**: Configure SPF records for your domain
- **DKIM**: Set up DKIM signing if using a custom domain
- **DMARC**: Implement DMARC policy for email authentication

## 📊 Features

### Password Reset Flow
1. **Request Reset**: User enters email address
2. **Token Generation**: Secure 32-character token generated
3. **Email Dispatch**: Branded email sent with reset link
4. **Token Validation**: Link validates token and expiration
5. **Password Update**: User sets new password
6. **Token Cleanup**: Used tokens are marked and cleaned up

### Security Features
- ✅ **1-hour expiration**: Reset links expire after 1 hour
- ✅ **Single use**: Each token can only be used once
- ✅ **Secure tokens**: Cryptographically secure random tokens
- ✅ **Rate limiting**: Prevents spam reset requests
- ✅ **Privacy protection**: Doesn't reveal if email exists
- ✅ **Automatic cleanup**: Expired tokens are automatically removed

### Email Template Features
- ✅ **Responsive design**: Works on all devices
- ✅ **Branded styling**: Matches Smart Split design
- ✅ **Clear instructions**: Step-by-step guidance
- ✅ **Security warnings**: User education about link expiration
- ✅ **Support contact**: Direct link to support email

## 🆘 Support

If you encounter issues with email setup:

1. **Check logs**: Look at application logs for error messages
2. **Test configuration**: Use the testing steps above
3. **Contact support**: Email [mail@stephanevdb.com](mailto:mail@stephanevdb.com) with:
   - Error messages
   - Email provider
   - Configuration (without passwords)
   - Steps you've tried

---

**Smart Split** - Making expense sharing simple and smart! 💰✨ 