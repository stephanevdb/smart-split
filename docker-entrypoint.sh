#!/bin/bash
set -e

echo "🚀 Starting Smart Split application..."

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