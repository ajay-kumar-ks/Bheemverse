import glob
import os
import aiosqlite

try:
    from backend.config import settings
except ImportError:
    from config import settings

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), settings.DB_PATH))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql"))
MIGRATIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "migrations"))


def _ensure_database_path() -> None:
    directory = os.path.dirname(DB_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


async def _execute_schema(db: aiosqlite.Connection) -> None:
    cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' LIMIT 1")
    row = await cursor.fetchone()
    if row is not None:
        return

    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()
    await db.executescript(schema_sql)
    await db.commit()


async def _ensure_migrations_table(db: aiosqlite.Connection) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS _migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )
    await db.commit()


async def _get_applied_migrations(db: aiosqlite.Connection) -> set[str]:
    cursor = await db.execute("SELECT name FROM _migrations")
    rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def _apply_migration(db: aiosqlite.Connection, name: str, path: str) -> None:
    with open(path, "r", encoding="utf-8") as migration_file:
        migration_sql = migration_file.read()

    statements = [stmt.strip() for stmt in migration_sql.split(";") if stmt.strip()]
    for statement in statements:
        try:
            await db.execute(statement)
        except aiosqlite.OperationalError as exc:
            message = str(exc).lower()
            if "duplicate column name" in message or "already exists" in message:
                continue
            raise

    await db.execute(
        "INSERT INTO _migrations (name) VALUES (?)",
        (name,),
    )
    await db.commit()


async def _run_migrations(db: aiosqlite.Connection) -> None:
    await _ensure_migrations_table(db)
    applied = await _get_applied_migrations(db)
    migration_files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    for migration_path in migration_files:
        migration_name = os.path.basename(migration_path)
        if migration_name in applied:
            continue
        await _apply_migration(db, migration_name, migration_path)


async def init_db(app) -> None:
    _ensure_database_path()
    app.state.db = await aiosqlite.connect(DB_PATH)
    await app.state.db.execute("PRAGMA foreign_keys=ON;")
    await app.state.db.execute("PRAGMA journal_mode=WAL;")
    await app.state.db.commit()
    await _execute_schema(app.state.db)
    await _run_migrations(app.state.db)


async def close_db(app) -> None:
    db = getattr(app.state, "db", None)
    if db is not None:
        await db.close()
