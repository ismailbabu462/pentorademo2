import sqlite3

conn = sqlite3.connect("/app/pentest_suite.db")
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
logger.info("Tables:", [table[0] for table in tables])

# Get record counts for each table
for table in tables:
    # SECURITY: Use parameterized query to prevent SQL injection
    table_name = table[0]
    # SECURITY: Validate table name against whitelist
    allowed_tables = ["users", "projects", "targets", "notes", "license_keys"]
    if table_name in allowed_tables:
        cursor.execute("SELECT COUNT(*) FROM ?", (table_name,))
        count = cursor.fetchone()[0]
        logger.info(f"{table_name}: {count} records")
    else:
        logger.info(f"{table_name}: [SKIPPED - Not in whitelist]")

# Get sample data from projects table
if "projects" in [table[0] for table in tables]:
    cursor.execute("SELECT id, name, description, user_id, created_at FROM projects")
    projects = cursor.fetchall()
    logger.info("\nProjects:")
    for project in projects:
        logger.info(f"  ID: {project[0]}")
        logger.info(f"  Name: {project[1]}")
        logger.info(f"  Description: {project[2]}")
        logger.info(f"  User ID: {project[3]}")
        logger.info(f"  Created: {project[4]}")
        logger.info("")

# Get sample data from users table
if "users" in [table[0] for table in tables]:
    cursor.execute("SELECT id, username, email, tier, created_at FROM users")
    users = cursor.fetchall()
    logger.info("Users:")
    for user in users:
        logger.info(f"  ID: {user[0]}")
        logger.info(f"  Username: {user[1]}")
        logger.info(f"  Email: {user[2]}")
        logger.info(f"  Tier: {user[3]}")
        logger.info(f"  Created: {user[4]}")
        logger.info("")

conn.close()
