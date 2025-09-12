# Smart Split - Docker Setup

This document explains how to run the Smart Split application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Architecture

The application consists of three main services:

1. **PostgreSQL Database** - Stores user data and application state
2. **Backend API** - Go-based REST API server
3. **Frontend** - Vue.js SPA served by Nginx

## Quick Start

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd smart-split-vite
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

4. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f backend
   docker-compose logs -f frontend
   docker-compose logs -f postgres
   ```

## Service Details

### PostgreSQL Database
- **Port:** 5432
- **Database:** smart_split
- **Username:** postgres
- **Password:** postgres
- **Volume:** postgres_data (persistent)

### Backend API
- **Port:** 8145
- **Language:** Go 1.21
- **Framework:** Gin
- **Health Check:** `/api/health`
- **Dependencies:** PostgreSQL

### Frontend
- **Port:** 3000
- **Framework:** Vue.js 3 + Vite
- **Build Tool:** Vite
- **Web Server:** Nginx
- **Health Check:** `/health`

## Environment Variables

### Backend Environment Variables
- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)
- `DB_USER` - Database username (default: postgres)
- `DB_PASSWORD` - Database password (default: postgres)
- `DB_NAME` - Database name (default: smart_split)
- `SERVER_HOST` - Server host (default: 0.0.0.0)
- `SERVER_PORT` - Server port (default: 8145)
- `ALLOWED_CORS_ORIGINS` - CORS allowed origins

## Development Workflow

### Rebuilding Services
```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Rebuild all services
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

### Accessing Services
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8145
- **Database:** localhost:5432

### Database Access
```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d smart_split

# View database logs
docker-compose logs postgres
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Ensure ports 3000, 8145, and 5432 are available
   - Change ports in docker-compose.yml if needed

2. **Database connection issues:**
   - Wait for PostgreSQL to be healthy before starting backend
   - Check database logs: `docker-compose logs postgres`

3. **Build failures:**
   - Clear Docker cache: `docker system prune -a`
   - Rebuild without cache: `docker-compose build --no-cache`

### Health Checks
All services include health checks. Monitor them with:
```bash
docker-compose ps
```

### Logs and Debugging
```bash
# Follow logs in real-time
docker-compose logs -f [service-name]

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## Production Considerations

### Security
- Change default database credentials
- Use environment variables for sensitive data
- Consider using Docker secrets for production

### Performance
- The current setup uses Alpine Linux for minimal image size
- Nginx is configured with gzip compression
- Static assets are cached with appropriate headers

### Scaling
- PostgreSQL can be replaced with managed database service
- Backend can be scaled horizontally behind a load balancer
- Frontend can be served from CDN

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: destroys data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

## Cleanup

```bash
# Remove all containers, networks, and images
docker-compose down --rmi all --volumes --remove-orphans

# Remove all unused Docker resources
docker system prune -a
```

## Support

For issues related to:
- **Docker setup:** Check this README and Docker logs
- **Application functionality:** Check the main project README
- **Database issues:** Check PostgreSQL logs and connection settings
