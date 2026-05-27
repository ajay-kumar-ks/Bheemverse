import asyncio

from fastapi import FastAPI

from database import init_db, close_db
from database import DB_PATH


async def main() -> None:
    app = FastAPI()
    await init_db(app)
    print(f"Database initialized at {DB_PATH}")
    await close_db(app)


if __name__ == "__main__":
    asyncio.run(main())
