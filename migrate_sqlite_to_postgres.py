import sqlite3
import asyncio
from pathlib import Path

import asyncpg

SQLITE_DB = Path('qera/database/qera.db')
PG_URL = 'postgresql://neondb_owner:npg_EF9LOigIS5qm@ep-sweet-mountain-apbqij2a-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require'

COPY_TABLES = [
    'users',
    'tags',
    'questions',
    'question_options',
    'exams',
    'exam_attempts',
    'question_likes',
    'bookmarks',
    'question_tags',
    'exam_questions',
    'comments',
    'notifications',
    'leaderboard',
]


def get_sqlite_columns(conn, table_name):
    cur = conn.execute(f"PRAGMA table_info('{table_name}')")
    return [row[1] for row in cur.fetchall()]


async def get_pg_columns(conn, table_name):
    rows = await conn.fetch(
        "SELECT column_name FROM information_schema.columns WHERE table_name = $1 ORDER BY ordinal_position",
        table_name,
    )
    return [row['column_name'] for row in rows]


async def table_count_pg(conn, table_name):
    return await conn.fetchval(f'SELECT COUNT(*) FROM "{table_name}"')


async def set_sequence(conn, table_name):
    seq_row = await conn.fetchrow(
        "SELECT pg_get_serial_sequence($1, 'id') AS seq",
        table_name,
    )
    if seq_row and seq_row['seq']:
        max_id = await conn.fetchval(f'SELECT MAX(id) FROM "{table_name}"')
        if max_id is None:
            max_id = 0
        await conn.execute(f"SELECT setval($1, $2, true)", seq_row['seq'], max_id)
        print(f'Updated sequence for {table_name} to {max_id}')


async def migrate_table(sqlite_conn, pg_conn, table_name):
    sqlite_cols = get_sqlite_columns(sqlite_conn, table_name)
    pg_cols = await get_pg_columns(pg_conn, table_name)
    copy_cols = [col for col in pg_cols if col in sqlite_cols]
    if not copy_cols:
        raise RuntimeError(f'No common columns found for {table_name}')

    quoted_cols = [f'"{c}"' for c in copy_cols]
    src_rows = sqlite_conn.execute(
        f'SELECT {", ".join(quoted_cols)} FROM "{table_name}"'
    ).fetchall()
    if not src_rows:
        print(f'Skipping {table_name}: source table is empty')
        return

    dest_count = await table_count_pg(pg_conn, table_name)
    if dest_count != 0:
        if dest_count == len(src_rows):
            print(f'Skipping {table_name}: target already contains {dest_count} rows')
            return
        raise RuntimeError(f'Target table {table_name} is not empty: {dest_count} rows')

    placeholders = ', '.join(f'${i+1}' for i in range(len(copy_cols)))
    insert_sql = f'INSERT INTO "{table_name}" ({", ".join(quoted_cols)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
    values = [tuple(row) for row in src_rows]

    async with pg_conn.transaction():
        for row in values:
            await pg_conn.execute(insert_sql, *row)
    print(f'Copied {len(values)} rows into {table_name}')

    if 'id' in copy_cols:
        await set_sequence(pg_conn, table_name)


async def main():
    if not SQLITE_DB.exists():
        raise FileNotFoundError(f'SQLite DB not found at {SQLITE_DB}')

    sqlite_conn = sqlite3.connect(SQLITE_DB)
    try:
        pg_conn = await asyncpg.connect(PG_URL)
        try:
            for table in COPY_TABLES:
                await migrate_table(sqlite_conn, pg_conn, table)
            print('Data migration completed successfully.')
        finally:
            await pg_conn.close()
    finally:
        sqlite_conn.close()


if __name__ == '__main__':
    asyncio.run(main())
