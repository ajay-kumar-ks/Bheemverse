import sqlite3
import asyncio
import asyncpg
from pathlib import Path

sqlite_path = Path('qera/database/qera.db')
url = 'postgresql://neondb_owner:npg_EF9LOigIS5qm@ep-sweet-mountain-apbqij2a-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require'
core_tables = ['users', 'questions', 'question_likes', 'question_options', 'bookmarks', 'question_tags', 'tags', 'exams', 'exam_questions', 'exam_attempts', 'leaderboard', 'comments', 'notifications']

print('SQLite path', sqlite_path.exists())
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()
for t in core_tables:
    cur.execute(f"PRAGMA table_info('{t}')")
    cols = [row[1] for row in cur.fetchall()]
    print('sqlite', t, cols)
conn.close()


async def main():
    conn = await asyncpg.connect(url)
    for t in core_tables:
        rows = await conn.fetch(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{t}' ORDER BY ordinal_position")
        cols = [r['column_name'] for r in rows]
        print('pg', t, cols)
    await conn.close()

asyncio.run(main())
