#!/bin/bash

# Permission fix script for Smart Split Docker setup
# Run this script on the host machine before starting Docker containers

echo "🔧 Fixing permissions for Smart Split Docker setup..."

# Create directories if they don't exist
mkdir -p data uploads

# Get current user info
CURRENT_USER=$(id -un)
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

echo "👤 Current user: $CURRENT_USER (uid: $CURRENT_UID, gid: $CURRENT_GID)"

# Option 1: Make directories writable by the Docker container user (999)
echo "🔧 Setting up permissions for Docker container (uid: 999)..."

# Try different permission strategies
if sudo -n true 2>/dev/null; then
    echo "📝 Using sudo to set proper ownership..."
    sudo chown -R 999:999 data/ uploads/ 2>/dev/null || {
        echo "⚠️  Could not change ownership with sudo, trying chmod..."
        sudo chmod -R 777 data/ uploads/
    }
else
    echo "📝 No sudo access, using chmod to make directories writable..."
    chmod 777 data/ uploads/ 2>/dev/null || {
        echo "❌ Could not fix permissions. Please run:"
        echo "   sudo chown -R 999:999 data/ uploads/"
        echo "   OR"
        echo "   sudo chmod 777 data/ uploads/"
        exit 1
    }
fi

echo "✅ Permissions fixed! You can now run:"
echo "   docker compose up --build smart-split" 