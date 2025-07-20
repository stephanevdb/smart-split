# 💰 Smart Split - Expense Sharing PWA

A modern Progressive Web App (PWA) for splitting expenses with friends and groups. Track shared costs, scan receipts with AI, and settle up easily.

## ✨ Features

### 🔐 User Management
- Secure user registration and authentication
- Personal profiles with bank details (IBAN/BIC)
- Password hashing with werkzeug security

### 👥 Group Management
- Create expense groups with custom names and descriptions
- Invite friends via unique invite codes or QR codes
- Join groups using invite links
- Group admin controls

### 💸 Expense Tracking
- Add expenses with custom descriptions and amounts
- Split costs among group members
- Automatic balance calculations
- Track who owes what to whom

### 🤖 AI-Powered Receipt Scanning
- Upload receipt photos for automatic expense extraction
- Powered by Google Gemini AI
- Select specific items from receipts to add as expenses
- Smart text recognition and amount parsing

### 📊 Dashboard & Analytics
- Personal dashboard with expense overview
- Balance summaries (what you owe vs. what you're owed)
- Recent activity tracking
- Group statistics

### 📱 Progressive Web App
- Install on any device like a native app
- Offline functionality with service worker
- Responsive design for mobile and desktop
- Push notification support

### 🏦 Settlement Features
- Calculate optimal debt settlements
- Bank details integration for easy transfers
- Settlement history tracking

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with connection pooling
- **Authentication**: Flask-Login with secure sessions
- **Forms**: WTForms with CSRF protection
- **AI Integration**: Google Gemini API for receipt scanning
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **PWA**: Service Worker, Web App Manifest
- **Deployment**: Docker, Gunicorn
- **QR Codes**: qrcode library for invite generation

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd smart-split
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start with Docker**:
   ```bash
   # Production mode
   ./docker-start.sh
   
   # Development mode
   ./docker-start.sh dev
   ```

4. **Access the app**: Open http://localhost:3000

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   export SECRET_KEY="your-secret-key"
   export GEMINI_API_KEY="your-gemini-api-key"  # Optional
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## 📋 Environment Variables

Create a `.env` file with the following variables:

```env
# Required
SECRET_KEY=your-very-secure-secret-key-here

# Optional - for AI receipt scanning
GEMINI_API_KEY=your-google-gemini-api-key

# Optional - database path (defaults to splitwise.db)
DATABASE=splitwise.db
```

## 🐳 Docker Deployment

### Production
```bash
docker compose up -d --build
```

### Development
```bash
docker compose --profile development up --build smart-split-dev
```

The application will be available at:
- Production: http://localhost:3077
- Development: http://localhost:3000

### Volumes
- `./data` - SQLite database persistence
- `./uploads` - Receipt image storage

## 📖 Usage Guide

### Getting Started
1. **Register** a new account or **login** with existing credentials
2. **Create a group** for your shared expenses (e.g., "Weekend Trip")
3. **Invite friends** using the generated invite code or QR code
4. **Add expenses** manually or by scanning receipts

### Adding Expenses
- **Manual Entry**: Enter description, amount, and select who paid
- **Receipt Scanning**: Upload a photo, let AI extract items, select what to include
- **Cost Splitting**: Expenses are automatically split among group members

### Managing Groups
- **View Group Details**: See all expenses, members, and balances
- **Group Admin**: Invite/remove members, manage group settings
- **Leave Group**: Exit groups you no longer need

### Settling Up
- **View Balances**: Dashboard shows what you owe and what you're owed
- **Settlement Suggestions**: App calculates optimal payment paths
- **Bank Integration**: Add IBAN/BIC for easy bank transfers

## 🔧 Features Overview

### Core Routes
- `/` - Home page with authentication
- `/dashboard` - Personal expense overview
- `/groups` - Group management
- `/groups/create` - Create new groups
- `/groups/{id}` - Group details and expenses
- `/groups/{id}/add_expense` - Add new expenses
- `/groups/{id}/scan_receipt` - AI receipt scanning
- `/settings` - User profile and bank details

### API Endpoints
- User authentication (login/register/logout)
- Group CRUD operations
- Expense management
- Receipt processing with AI
- Balance calculations
- QR code generation

### Database Schema
- **Users**: Authentication and profile data
- **Groups**: Expense groups with invite codes
- **Group Members**: Many-to-many user-group relationships
- **Expenses**: Individual expense records
- **Expense Splits**: How expenses are divided among members

## 🔒 Security Features

- Password hashing with werkzeug
- CSRF protection on all forms
- Secure session management
- Input validation and sanitization
- SQL injection prevention
- File upload restrictions (7MB limit)

## 📱 PWA Features

- **Installable**: Add to home screen on mobile devices
- **Offline Support**: Basic functionality without internet
- **Responsive Design**: Works on all screen sizes
- **Fast Loading**: Service worker caching
- **App-like Experience**: Full-screen mode, custom icons

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Docker documentation](DOCKER.md) for deployment issues
2. Ensure all environment variables are properly set
3. Verify that the uploads and data directories are writable
4. Check the application logs for detailed error messages

## 🚀 Roadmap

- [ ] Mobile app versions (React Native/Flutter)
- [ ] Multiple currency support
- [ ] Advanced expense categories
- [ ] Email notifications
- [ ] Export functionality (PDF/CSV)
- [ ] Integration with banking APIs
- [ ] Advanced analytics and reporting

---

**Smart Split** - Making expense sharing simple and smart! 💰✨
