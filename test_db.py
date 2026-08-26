import asyncio
from sqlalchemy import text
from database import engine


async def test_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(
                text("SELECT 1")
            )

            print("PostgreSQL connection successful!")
            print("Result:", result.scalar())

    except Exception as e:
        print("Database connection failed:")
        print(e)

    finally:
        await engine.dispose()


asyncio.run(test_connection())