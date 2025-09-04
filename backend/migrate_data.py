#!/usr/bin/env python3
"""
Data Migration Script: SQLite to MySQL
Transfers all data from SQLite database to MySQL database.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Import our models and configs
from database import Base, User, Project, Target, Note, LicenseKey, ToolOutput, Vulnerability
from config import DATABASE_URL, MYSQL_DATABASE_URL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_engines():
    """Create SQLite and MySQL engines."""
    # SQLite source engine
    sqlite_url = "sqlite:///./pentest_suite.db"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    
    # MySQL destination engine
    mysql_url = os.getenv("MYSQL_DATABASE_URL", MYSQL_DATABASE_URL)
    mysql_engine = create_engine(mysql_url, pool_pre_ping=True, pool_recycle=300)
    
    return sqlite_engine, mysql_engine

def create_sessions(sqlite_engine, mysql_engine):
    """Create database sessions."""
    SqliteSession = sessionmaker(bind=sqlite_engine)
    MysqlSession = sessionmaker(bind=mysql_engine)
    
    return SqliteSession(), MysqlSession()

def migrate_table_data(sqlite_session, mysql_session, model_class, table_name):
    """Generic function to migrate data from one table to another."""
    logger.info(f"Migrating {table_name} table...")
    
    try:
        # Get all data from SQLite
        sqlite_data = sqlite_session.query(model_class).all()
        logger.info(f"Found {len(sqlite_data)} records in {table_name}")
        
        if not sqlite_data:
            logger.info(f"No data to migrate for {table_name}")
            return True
        
        # Convert SQLAlchemy objects to dictionaries
        migrated_count = 0
        
        for record in sqlite_data:
            # Create a dictionary of the record's attributes
            record_dict = {}
            for column in model_class.__table__.columns:
                value = getattr(record, column.name)
                record_dict[column.name] = value
            
            # Create new record in MySQL
            try:
                new_record = model_class(**record_dict)
                mysql_session.merge(new_record)  # Use merge to handle duplicates
                migrated_count += 1
                
                if migrated_count % 100 == 0:  # Log progress for large datasets
                    logger.info(f"Migrated {migrated_count} records from {table_name}")
                    
            except Exception as e:
                logger.error(f"Error migrating record from {table_name}: {e}")
                logger.error(f"Record data: {record_dict}")
                continue
        
        # Commit the changes
        mysql_session.commit()
        logger.info(f"Successfully migrated {migrated_count} records from {table_name}")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating {table_name}: {e}")
        mysql_session.rollback()
        return False

def verify_migration(sqlite_session, mysql_session, model_class, table_name):
    """Verify that migration was successful by comparing record counts."""
    try:
        sqlite_count = sqlite_session.query(model_class).count()
        mysql_count = mysql_session.query(model_class).count()
        
        logger.info(f"{table_name}: SQLite={sqlite_count}, MySQL={mysql_count}")
        
        if sqlite_count == mysql_count:
            logger.info(f"✅ {table_name} migration verified successfully")
            return True
        else:
            logger.error(f"❌ {table_name} migration failed: count mismatch")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying {table_name}: {e}")
        return False

def main():
    """Main migration function."""
    logger.info("Starting SQLite to MySQL data migration...")
    
    try:
        # Create engines and sessions
        sqlite_engine, mysql_engine = create_engines()
        sqlite_session, mysql_session = create_sessions(sqlite_engine, mysql_engine)
        
        # Create tables in MySQL if they don't exist
        logger.info("Creating MySQL tables...")
        Base.metadata.create_all(mysql_engine)
        
        # Define migration order (respect foreign key dependencies)
        migration_plan = [
            (User, "users"),
            (Project, "projects"),
            (Target, "targets"),
            (Note, "notes"),
            (LicenseKey, "license_keys"),
            (ToolOutput, "tool_outputs"),
            (Vulnerability, "vulnerabilities"),
        ]
        
        # Migrate data
        success_count = 0
        total_tables = len(migration_plan)
        
        for model_class, table_name in migration_plan:
            if migrate_table_data(sqlite_session, mysql_session, model_class, table_name):
                success_count += 1
            else:
                logger.error(f"Failed to migrate {table_name}")
        
        logger.info(f"Migration completed: {success_count}/{total_tables} tables successful")
        
        # Verify migration
        logger.info("Verifying migration...")
        verification_success = 0
        
        for model_class, table_name in migration_plan:
            if verify_migration(sqlite_session, mysql_session, model_class, table_name):
                verification_success += 1
        
        logger.info(f"Verification completed: {verification_success}/{total_tables} tables verified")
        
        if success_count == total_tables and verification_success == total_tables:
            logger.info("🎉 Data migration completed successfully!")
            return True
        else:
            logger.error("❌ Data migration completed with errors")
            return False
            
    except Exception as e:
        logger.error(f"Fatal error during migration: {e}")
        return False
    
    finally:
        # Close sessions
        try:
            sqlite_session.close()
            mysql_session.close()
        except:
            pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
