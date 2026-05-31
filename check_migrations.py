import asyncio
import asyncpg
import sys
import os

# Database URL from environment or parameter
DATABASE_URL = "postgresql://neondb_owner:npg_EF9LOigIS5qm@ep-sweet-mountain-apbqij2a-pooler.c-7.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

# Expected migrations (from migrations folder)
EXPECTED_MIGRATIONS = [
    "0001_create_migrations_table.sql",
    "0002_add_user_suspended_and_question_flag.sql",
    "0003_add_exam_attempt_and_metadata_columns.sql",
    "0004_repair_exam_attempt_resume_columns.sql",
    "0005_mark_legacy_attempts_submitted.sql",
    "0006_add_media_and_profile_fields.sql",
]


async def check_migration_status():
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Successfully connected to PostgreSQL database")
        print(f"  Database: {DATABASE_URL.split('/')[-1].split('?')[0]}")
        print()

        # Check if _migrations table exists
        result = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = '_migrations'
            );
            """
        )

        if not result:
            print("⚠ _migrations table does not exist yet!")
            await conn.close()
            return

        print("✓ _migrations table exists")
        print()

        # Get applied migrations
        applied = await conn.fetch(
            "SELECT name, applied_at FROM _migrations ORDER BY applied_at;"
        )

        print(f"Applied Migrations ({len(applied)}/{len(EXPECTED_MIGRATIONS)}):")
        print("-" * 70)

        applied_names = set()
        for row in applied:
            applied_names.add(row['name'])
            print(f"  ✓ {row['name']:<50} {row['applied_at']}")

        print()
        print("Expected Migrations Status:")
        print("-" * 70)

        all_completed = True
        for migration in EXPECTED_MIGRATIONS:
            if migration in applied_names:
                print(f"  ✓ {migration}")
            else:
                print(f"  ✗ {migration} (NOT APPLIED)")
                all_completed = False

        print()
        print("=" * 70)
        if all_completed and len(applied) == len(EXPECTED_MIGRATIONS):
            print("✓ ALL MIGRATIONS COMPLETED!")
        else:
            pending = len(EXPECTED_MIGRATIONS) - len(applied)
            print(f"⚠ Migrations pending: {pending}/{len(EXPECTED_MIGRATIONS)}")

        await conn.close()

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_migration_status())
