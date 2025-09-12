# Smart Split Backend API

A simple Go REST API built with Gin framework.

## Features

- Health check endpoint
- CORS enabled for frontend integration
- Simple and lightweight

## Prerequisites

- Go 1.21 or higher

## Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   go mod tidy
   ```

3. Run the server:
   ```bash
   go run main.go
   ```

The API will start on `http://localhost:8145`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns the API status and version

### Root
- **GET** `/`
- Returns API information and available endpoints

## Development

To add new routes, modify the `main.go` file and add new handlers as needed.

## CORS Configuration

The API is configured to allow requests from:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Common React dev server)
- `http://127.0.0.1:5173` (Vite dev server alternative)
