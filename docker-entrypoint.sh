#!/bin/bash
set -e

echo "🚀 Starting Smart Split application..."

# Fix permissions for mounted volumes if needed
echo "🔧 Checking and fixing permissions..."
if [ -d "/app/data" ]; then
    # Try to make the directory writable
    chmod u+w /app/data 2>/dev/null || echo "⚠️  Could not fix /app/data permissions (this is expected on some systems)"
fi

if [ -d "/app/uploads" ]; then
    # Try to make the directory writable
    chmod u+w /app/uploads 2>/dev/null || echo "⚠️  Could not fix /app/uploads permissions (this is expected on some systems)"
fi

# Initialize the application (database, directories, etc.)
echo "🔧 Running application initialization..."
python startup.py

# Check if we're in development mode
if [ "$FLASK_ENV" = "development" ]; then
    echo "🔧 Starting in DEVELOPMENT mode..."
    exec python app.py
else
    echo "🏭 Starting in PRODUCTION mode with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:3000 --workers 4 --timeout 120 --access-logfile - --error-logfile - app:app
fi 