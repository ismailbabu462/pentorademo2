#!/usr/bin/env python3
"""
Database Migration Script
Handles database migrations and schema updates for production deployment
"""

import logging
import os
import sys
import time
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from alembic import command
from alembic.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def wait_for_database(database_url, max_retries=30, retry_delay=2):
    """Wait for database to be ready"""
    logger.info("🔄 Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database is ready!")
            return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ Database not ready after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    return False


def run_migrations(database_url):
    """Run Alembic migrations"""
    logger.info("🔄 Running database migrations...")
    
    try:
        # Set up Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database migrations completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def create_database_if_not_exists(database_url):
    """Create database if it doesn't exist (MySQL only)"""
    if not database_url.startswith("mysql"):
        return True
    
    try:
        # Extract database name from URL
        # Format: mysql+pymysql://user:pass@host:port/dbname
        db_name = database_url.split("/")[-1]
        base_url = "/".join(database_url.split("/")[:-1])
        
        # Connect without database name
        engine = create_engine(base_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Create database if it doesn't exist
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        logger.info(f"✅ Database '{db_name}' created or already exists")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False


def verify_database_schema(database_url):
    """Verify database schema is correct"""
    logger.info("🔄 Verifying database schema...")
    
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Check if required tables exist
            required_tables = ['users', 'devices', 'projects', 'targets', 'vulnerabilities', 'notes']
            
            for table in required_tables:
                result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                if not result.fetchone():
                    logger.error(f"❌ Required table '{table}' not found")
                    return False
            
            logger.info("✅ Database schema verification passed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        return False


def main():
    """Main migration function"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    logger.info(f"📊 Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    # Step 1: Wait for database to be ready
    if not wait_for_database(database_url):
        logger.error("❌ Database is not ready. Exiting...")
        sys.exit(1)
    
    # Step 2: Create database if it doesn't exist (MySQL only)
    if not create_database_if_not_exists(database_url):
        logger.error("❌ Failed to create database. Exiting...")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_migrations(database_url):
        logger.error("❌ Migration failed. Exiting...")
        sys.exit(1)
    
    # Step 4: Verify schema
    if not verify_database_schema(database_url):
        logger.error("❌ Schema verification failed. Exiting...")
        sys.exit(1)
    
    logger.info("🎉 Database migration completed successfully!")


if __name__ == "__main__":
    main()
