#!/usr/bin/env python3
"""
Startup script for Smart Split application.
This script ensures proper initialization before starting the Flask app.
"""

import os
import sys
import logging
from app import init_db, ensure_upload_folder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_application():
    """Initialize the application before starting the server."""
    try:
        logger.info("🚀 Starting Smart Split application initialization...")
        
        # Ensure upload folder exists
        logger.info("📁 Creating upload directories...")
        ensure_upload_folder()
        
        # Initialize database
        logger.info("🗄️  Initializing database...")
        init_db()
        
        logger.info("✅ Application initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_application() 