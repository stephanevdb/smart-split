#!/bin/bash

# Docker startup script for Smart Split app

set -e

echo "🚀 Starting Smart Split Docker containers..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    echo "   Especially set your GEMINI_API_KEY if you want AI features."
    exit 1
fi

# Determine which environment to run
ENVIRONMENT=${1:-production}

if [ "$ENVIRONMENT" = "dev" ] || [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Starting in DEVELOPMENT mode..."
    docker compose --profile development up --build smart-split-dev
else
    echo "🏭 Starting in PRODUCTION mode..."
    docker compose up --build smart-split
fi 