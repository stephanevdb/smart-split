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
        
        # Check current user and permissions
        import pwd
        user_info = pwd.getpwuid(os.getuid())
        logger.info(f"👤 Running as user: {user_info.pw_name} (uid: {os.getuid()})")
        
        # Ensure upload folder exists
        logger.info("📁 Creating upload directories...")
        ensure_upload_folder()
        
        # Check database directory permissions
        import app
        db_path = app.app.config['DATABASE']
        db_dir = os.path.dirname(db_path)
        logger.info(f"🗄️  Database path: {db_path}")
        logger.info(f"📂 Database directory: {db_dir}")
        
        # Create database directory if it doesn't exist
        if not os.path.exists(db_dir):
            logger.info(f"📁 Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # Check if we can write to the database directory
        if not os.access(db_dir, os.W_OK):
            logger.error(f"❌ No write permission to database directory: {db_dir}")
            logger.error("🔧 Please run on the host machine:")
            logger.error("   sudo chown -R 999:999 data/ uploads/")
            logger.error("   OR chmod 777 data/ uploads/")
            logger.error("   OR run ./fix-permissions.sh")
            # Try to fix permissions (but this usually won't work in Docker)
            try:
                os.chmod(db_dir, 0o755)
                logger.info("🔧 Fixed directory permissions")
            except Exception as perm_error:
                logger.error(f"❌ Could not fix permissions: {perm_error}")
                raise
        
        # Initialize database
        logger.info("🗄️  Initializing database...")
        init_db()
        
        logger.info("✅ Application initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
        import traceback
        logger.error(f"📋 Full error traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_application() 