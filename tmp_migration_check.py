import sqlite3
import pathlib
import asyncio

import asyncpg

sqlite_path = pathlib.Path('qera/database/qera.db')
print('SQLite exists:', sqlite_path.exists())
if sqlite_path.exists():
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]
    print('SQLite tables:', tables)
    for t in tables:
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"')
            print('sqlite', t, cur.fetchone()[0])
        except Exception as e:
            print('sqlite err', t, e)
    conn.close()


def pg_check():
    url = 'postgresql://neondb_owner:npg_EF9LOigIS5qm@ep-sweet-mountain-apbqij2a-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require'
    return asyncpg.connect(url)


async def main():
    try:
        conn = await pg_check()
    except Exception as e:
        print('Postgres connect error', e)
        return
    rows = await conn.fetch("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';")
    tables = [r[0] for r in rows]
    print('Postgres tables:', tables)
    for t in tables:
        try:
            c = await conn.fetchval(f'SELECT COUNT(*) FROM "{t}"')
            print('pg', t, c)
        except Exception as e:
            print('pg err', t, e)
    await conn.close()

asyncio.run(main())
