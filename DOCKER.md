# Docker Setup for Smart Split

This document explains how to run the Smart Split application using Docker.

## Quick Start

1. **Clone and setup environment**:
   ```bash
   git clone <your-repo>
   cd smart-split
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` file with your settings:
   ```bash
   # Required: Change the secret key
   SECRET_KEY=your-very-secure-secret-key-here
   
   # Optional: Add your Gemini AI key for receipt scanning
   GEMINI_API_KEY=your-gemini-api-key
   ```

3. **Start the application**:
   ```bash
   # Production mode
   ./docker-start.sh
   
   # OR Development mode
   ./docker-start.sh dev
   ```

4. **Access the application**:
   Open http://localhost:3000 in your browser

## Docker Commands

### Production Deployment
```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d --build

# Stop
docker compose down

# View logs
docker compose logs -f smart-split
```

### Development Mode
```bash
# Start development environment with hot reloading
docker compose --profile development up --build smart-split-dev

# Run in background
docker compose --profile development up -d --build smart-split-dev
```

### Manual Docker Commands
```bash
# Build image manually
docker build -t smart-split .

# Run container manually
docker run -p 3000:3000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/uploads:/app/uploads \
  -e SECRET_KEY=your-secret-key \
  smart-split
```

## Volumes and Persistence

The application uses two important volumes for data persistence:

- `./data:/app/data` - SQLite database storage
- `./uploads:/app/uploads` - User uploaded files (receipts)

These directories will be automatically created and will persist your data between container restarts.

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | change-this-secret-key-in-production |
| `GEMINI_API_KEY` | Google Gemini AI API key for receipt scanning | No | None |
| `DATABASE` | Database file path | No | /app/data/splitwise.db |
| `FLASK_ENV` | Flask environment mode | No | production |

## Health Checks

The container includes health checks that verify the application is running correctly:
- Endpoint: `http://localhost:3000/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs smart-split

# Check if port is already in use
lsof -i :3000
```

### Database issues
```bash
# Reset database (WARNING: This will delete all data)
rm -rf data/
mkdir data
docker compose restart smart-split
```

### Permission issues
```bash
# The container runs as uid:999, so fix permissions accordingly:

# Option 1: Use the helper script
./fix-permissions.sh

# Option 2: Manual fix with sudo
sudo chown -R 999:999 data/ uploads/

# Option 3: Make directories world-writable (less secure but works)
chmod 777 data/ uploads/

# Option 4: Fix ownership to current user (alternative)
sudo chown -R $USER:$USER data uploads
```

### Development mode not working
```bash
# Ensure you're using the development profile
docker compose --profile development up smart-split-dev
```

## Security Notes

- The application runs as a non-root user (`appuser`) inside the container
- Database and uploads are stored in mounted volumes outside the container
- Always use a strong `SECRET_KEY` in production
- Consider using Docker secrets for sensitive environment variables in production

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (nginx, traefik) for SSL termination
2. **Set up log aggregation** for monitoring
3. **Use Docker secrets** for sensitive environment variables
4. **Regular backups** of the `data` directory
5. **Monitor resource usage** and adjust container limits as needed

Example with nginx reverse proxy:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - smart-split
``` 