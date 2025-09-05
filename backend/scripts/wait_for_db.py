#!/usr/bin/env python3
"""
Database connection wait script
Waits for database to be ready before starting the application
"""

import logging
import os
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def wait_for_database(database_url, max_retries=30, retry_delay=2):
    """
    Wait for database to be ready

    Args:
        database_url (str): Database connection URL
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Delay between retries in seconds

    Returns:
        bool: True if database is ready, False otherwise
    """
    logger.info(f"🔄 Waiting for database to be ready...")
    logger.info(
        f"📊 Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}"
    )

    for attempt in range(max_retries):
        try:
            # Create engine
            if database_url.startswith("sqlite"):
                engine = create_engine(
                    database_url, connect_args={"check_same_thread": False}
                )
            else:
                engine = create_engine(database_url, pool_pre_ping=True)

            # Test connection
            with engine.connect() as conn:
                from sqlalchemy import text

                conn.execute(text("SELECT 1"))

            logger.info("✅ Database is ready!")
            return True

        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"⚠️ Database not ready (attempt {attempt + 1}/{max_retries}): {e}"
                )
                logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"❌ Database not ready after {max_retries} attempts: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False

    return False


def main():
    """Main function"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./pentest_suite.db")

    if not wait_for_database(database_url):
        logger.error("❌ Failed to connect to database. Exiting...")
        sys.exit(1)

    logger.info("🚀 Database is ready. Starting application...")


if __name__ == "__main__":
    main()
