import sqlite3

conn = sqlite3.connect('/app/pentest_suite.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables:', [table[0] for table in tables])

# Get record counts for each table
for table in tables:
    # SECURITY: Use parameterized query to prevent SQL injection
    table_name = table[0]
    # SECURITY: Validate table name against whitelist
    allowed_tables = ['users', 'projects', 'targets', 'notes', 'license_keys']
    if table_name in allowed_tables:
        cursor.execute("SELECT COUNT(*) FROM ?", (table_name,))
        count = cursor.fetchone()[0]
        print(f'{table_name}: {count} records')
    else:
        print(f'{table_name}: [SKIPPED - Not in whitelist]')

# Get sample data from projects table
if 'projects' in [table[0] for table in tables]:
    cursor.execute("SELECT id, name, description, user_id, created_at FROM projects")
    projects = cursor.fetchall()
    print('\nProjects:')
    for project in projects:
        print(f'  ID: {project[0]}')
        print(f'  Name: {project[1]}')
        print(f'  Description: {project[2]}')
        print(f'  User ID: {project[3]}')
        print(f'  Created: {project[4]}')
        print()

# Get sample data from users table
if 'users' in [table[0] for table in tables]:
    cursor.execute("SELECT id, username, email, tier, created_at FROM users")
    users = cursor.fetchall()
    print('Users:')
    for user in users:
        print(f'  ID: {user[0]}')
        print(f'  Username: {user[1]}')
        print(f'  Email: {user[2]}')
        print(f'  Tier: {user[3]}')
        print(f'  Created: {user[4]}')
        print()

conn.close()
