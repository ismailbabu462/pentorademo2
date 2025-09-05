import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def check_projects():
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    # Check both databases
    for db_name in ["pentest_suite", "test_database"]:
        logger.info(f"\n=== Checking database: {db_name} ===")
        db = client[db_name]

        # Get all projects
        projects = await db.projects.find({}).to_list(1000)
        logger.info(f"Total projects in database: {len(projects)}")

        for project in projects:
            logger.info(
                f'Project: {project.get("name")} - User ID: {project.get("user_id")}'
            )

        # Get all users
        users = await db.users.find({}).to_list(1000)
        logger.info(f"Total users in database: {len(users)}")

        for user in users:
            logger.info(f'User: {user.get("username")} - ID: {user.get("id")}')

    client.close()


if __name__ == "__main__":
    asyncio.run(check_projects())
