import asyncio

from database import engine, Base
from models import Student, User


async def reset_database():
    async with engine.begin() as conn:
        print("Deleting old tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("Database reset successfully!")


asyncio.run(reset_database())