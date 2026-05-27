from typing import Optional


def row_to_user(row) -> Optional[dict]:
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "password_hash": row[3],
        "role": row[4],
        "avatar_url": row[5],
        "bio": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


async def create_user(db, name: str, email: str, password_hash: str, role: str = "student", avatar_url: Optional[str] = None, bio: Optional[str] = None) -> dict:
    cursor = await db.execute(
        """
        INSERT INTO users (name, email, password_hash, role, avatar_url, bio)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, email, password_hash, role, avatar_url, bio),
    )
    await db.commit()
    user_id = cursor.lastrowid
    return await get_user_by_id(db, user_id)


async def get_user_by_email(db, email: str) -> Optional[dict]:
    cursor = await db.execute(
        "SELECT id, name, email, password_hash, role, avatar_url, bio, created_at, updated_at FROM users WHERE email = ?",
        (email,),
    )
    row = await cursor.fetchone()
    return row_to_user(row)


async def get_user_by_id(db, user_id: int) -> Optional[dict]:
    cursor = await db.execute(
        "SELECT id, name, email, password_hash, role, avatar_url, bio, created_at, updated_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    return row_to_user(row)
