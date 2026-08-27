import asyncio

from database import engine, Base
from models import Student, User, Role, Permission


async def reset_database():
    async with engine.begin() as conn:
        print("Deleting old tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("Database reset successfully!")


if __name__ == "__main__":
    asyncio.run(reset_database())
