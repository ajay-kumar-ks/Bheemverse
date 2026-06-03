import argparse
import asyncio
import os
import re
import sqlite3
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent
SQLITE_DB_DEFAULT = ROOT / 'qera' / 'backend' / 'database_files' / 'qera.db'
SCHEMA_PATH = ROOT / 'qera' / 'backend' / 'database_files' / 'schema_postgres.sql'
MIGRATIONS_DIR = ROOT / 'qera' / 'backend' / 'database_files' / 'migrations'
SKIP_TABLES = {
    '_migrations',
    'sqlite_sequence',
}
TABLE_ORDER = [
    'users',
    'tags',
    'questions',
    'question_options',
    'question_tags',
    'exams',
    'exam_questions',
    'exam_attempts',
    'leaderboard',
    'comments',
    'comment_votes',
    'question_likes',
    'bookmarks',
    'notifications',
    'badges',
    'pending_approvals',
    'user_badges',
]


def get_sqlite_tables(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [row[0] for row in cursor.fetchall()]


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


def translate_postgres_sql(sql: str) -> str:
    original_sql = sql
    sql = re.sub(r"\bINSERT\s+OR\s+IGNORE\s+INTO\b", "INSERT INTO", sql, flags=re.I)
    if re.search(r"\bINSERT\s+OR\s+IGNORE\s+INTO\b", original_sql, flags=re.I):
        sql = sql.rstrip().rstrip(";")
        if "ON CONFLICT" not in sql.upper():
            sql += " ON CONFLICT DO NOTHING"

    sql = re.sub(r"datetime\(\s*'now'\s*\)", "CURRENT_TIMESTAMP::text", sql, flags=re.I)
    sql = re.sub(r"\bDATETIME\b", "TEXT", sql, flags=re.I)
    sql = re.sub(r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b", "SERIAL PRIMARY KEY", sql, flags=re.I)
    sql = re.sub(r"\bAUTOINCREMENT\b", "", sql, flags=re.I)
    return sql


async def execute_sql_file(conn, path: Path) -> None:
    sql = path.read_text(encoding='utf-8')
    sql = translate_postgres_sql(sql)
    statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
    for statement in statements:
        try:
            await conn.execute(statement)
        except asyncpg.PostgresError as exc:
            lower = str(exc).lower()
            if any(sub in lower for sub in [
                'duplicate column',
                'already exists',
                'duplicate table',
                'duplicate index',
                'relation "_migrations" already exists',
            ]):
                continue
            raise


async def init_postgres_schema(pg_conn):
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f'Postgres schema file not found: {SCHEMA_PATH}')
    print(f'Creating schema from {SCHEMA_PATH}')
    await execute_sql_file(pg_conn, SCHEMA_PATH)

    migration_paths = sorted(MIGRATIONS_DIR.glob('*.sql'))
    if migration_paths:
        print('Applying migration files:')
        for path in migration_paths:
            print(f'  - {path.name}')
            await execute_sql_file(pg_conn, path)


async def migrate_table(sqlite_conn, pg_conn, table_name):
    sqlite_cols = get_sqlite_columns(sqlite_conn, table_name)
    pg_cols = await get_pg_columns(pg_conn, table_name)
    copy_cols = [col for col in pg_cols if col in sqlite_cols]
    if not copy_cols:
        print(f'Skipping {table_name}: no shared columns')
        return

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
        print(f'Warning: target table {table_name} already contains {dest_count} rows; inserting missing rows only')

    placeholders = ', '.join(f'${i+1}' for i in range(len(copy_cols)))
    insert_sql = (
        f'INSERT INTO "{table_name}" ({", ".join(quoted_cols)}) VALUES ({placeholders}) '
        'ON CONFLICT DO NOTHING'
    )
    values = [tuple(row) for row in src_rows]

    async with pg_conn.transaction():
        for row in values:
            await pg_conn.execute(insert_sql, *row)

    print(f'Copied {len(values)} rows into {table_name}')
    if 'id' in copy_cols:
        await set_sequence(pg_conn, table_name)


async def main():
    parser = argparse.ArgumentParser(
        description='Migrate local SQLite data into a PostgreSQL database.',
    )
    parser.add_argument(
        '--sqlite',
        default=str(SQLITE_DB_DEFAULT),
        help='Path to local SQLite database file.',
    )
    parser.add_argument(
        '--postgres',
        default=os.getenv('DATABASE_URL'),
        help='PostgreSQL connection DSN. Defaults to DATABASE_URL environment variable.',
    )
    args = parser.parse_args()

    if not args.postgres:
        raise ValueError('PostgreSQL URL is required. Set DATABASE_URL or pass --postgres.')

    sqlite_db_path = Path(args.sqlite)
    if not sqlite_db_path.exists():
        raise FileNotFoundError(f'SQLite DB not found at {sqlite_db_path}')

    sqlite_conn = sqlite3.connect(sqlite_db_path)
    try:
        pg_conn = await asyncpg.connect(args.postgres)
        try:
            await init_postgres_schema(pg_conn)
            sqlite_tables = [
                table
                for table in get_sqlite_tables(sqlite_conn)
                if table not in SKIP_TABLES and not table.startswith('questions_fts')
            ]
            ordered_tables = [table for table in TABLE_ORDER if table in sqlite_tables]
            remaining_tables = [table for table in sqlite_tables if table not in ordered_tables]
            tables = ordered_tables + remaining_tables
            print('Tables to copy:', tables)
            for table in tables:
                await migrate_table(sqlite_conn, pg_conn, table)
            print('Data migration completed successfully.')
        finally:
            await pg_conn.close()
    finally:
        sqlite_conn.close()


if __name__ == '__main__':
    asyncio.run(main())
