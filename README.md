# Smart Split - Expense Sharing App

A full-stack expense sharing application built with Vite + PrimeVue frontend and Go backend.

## Project Structure

```
smart-split-vite/
├── frontend/          # Vue.js + Vite + PrimeVue frontend
├── backend/           # Go backend with Gin framework
└── README.md          # This file
```

## Features

- **User Management**: Create, read, update, and delete users
- **Expense Tracking**: Record and manage shared expenses
- **Group Management**: Organize users into groups for expense sharing
- **RESTful API**: Clean backend API for frontend integration
- **Modern UI**: Beautiful interface built with PrimeVue components

## Prerequisites

- Node.js (v18 or higher)
- Go (v1.21 or higher)
- npm or yarn

## Quick Start

### Backend (Go)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the Go server:
   ```bash
   go run main.go
   ```

The backend will start on `http://localhost:8080`

### Frontend (Vue.js + Vite)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will start on `http://localhost:5173`

## API Endpoints

### Users
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Expenses
- `GET /api/expenses` - Get all expenses
- `GET /api/expenses/:id` - Get expense by ID
- `POST /api/expenses` - Create new expense
- `PUT /api/expenses/:id` - Update expense
- `DELETE /api/expenses/:id` - Delete expense

### Groups
- `GET /api/groups` - Get all groups
- `GET /api/groups/:id` - Get group by ID
- `POST /api/groups` - Create new group
- `PUT /api/groups/:id` - Update group
- `DELETE /api/groups/:id` - Delete group

### Health Check
- `GET /api/health` - API health status

## Data Models

### User
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Expense
```json
{
  "id": 1,
  "description": "Dinner",
  "amount": 75.50,
  "paidBy": 1,
  "splitBetween": [1, 2, 3],
  "date": "2024-01-15"
}
```

### Group
```json
{
  "id": 1,
  "name": "Roommates",
  "users": [1, 2, 3]
}
```

## Technologies Used

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Fast build tool and dev server
- **PrimeVue** - Rich UI component library
- **PrimeIcons** - Icon library

### Backend
- **Go** - Fast and efficient programming language
- **Gin** - HTTP web framework
- **CORS** - Cross-origin resource sharing support

## Development

### Adding New Features

1. **Backend**: Add new routes and handlers in `backend/main.go`
2. **Frontend**: Create new Vue components in `frontend/src/components/`

### Building for Production

#### Frontend
```bash
cd frontend
npm run build
```

#### Backend
```bash
cd backend
go build -o smart-split-backend main.go
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
