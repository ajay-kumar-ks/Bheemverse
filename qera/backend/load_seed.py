import asyncio
from pathlib import Path
import aiosqlite

async def main() -> None:
    root = Path(__file__).resolve().parent.parent
    db_path = root / 'database' / 'qera.db'
    seed_path = root / 'database' / 'seeds' / 'dev_seed.sql'
    async with aiosqlite.connect(db_path) as db:
        sql = seed_path.read_text(encoding='utf-8')
        await db.executescript(sql)
        await db.commit()
    print(f'Seed data loaded into {db_path}')

if __name__ == '__main__':
    asyncio.run(main())
