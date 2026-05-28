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
        "is_suspended": bool(row[5]),
        "avatar_url": row[6],
        "bio": row[7],
        "created_at": row[8],
        "updated_at": row[9],
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
        "SELECT id, name, email, password_hash, role, is_suspended, avatar_url, bio, created_at, updated_at FROM users WHERE email = ?",
        (email,),
    )
    row = await cursor.fetchone()
    return row_to_user(row)


async def get_user_by_id(db, user_id: int) -> Optional[dict]:
    cursor = await db.execute(
        "SELECT id, name, email, password_hash, role, is_suspended, avatar_url, bio, created_at, updated_at FROM users WHERE id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    return row_to_user(row)


async def update_user(db, user_id: int, name: str | None = None, avatar_url: str | None = None, bio: str | None = None, is_suspended: bool | None = None) -> Optional[dict]:
    current = await get_user_by_id(db, user_id)
    if current is None:
        return None
    fields: list[str] = []
    values: list = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if avatar_url is not None:
        fields.append("avatar_url = ?")
        values.append(avatar_url)
    if bio is not None:
        fields.append("bio = ?")
        values.append(bio)
    if is_suspended is not None:
        fields.append("is_suspended = ?")
        values.append(int(is_suspended))
    if fields:
        values.append(user_id)
        await db.execute(f"UPDATE users SET {', '.join(fields)}, updated_at = datetime('now') WHERE id = ?", tuple(values))
        await db.commit()
    return await get_user_by_id(db, user_id)


async def get_user_profile(db, user_id: int) -> Optional[dict]:
    user = await get_user_by_id(db, user_id)
    if user is None:
        return None

    cursor = await db.execute("SELECT COUNT(*) FROM questions WHERE user_id = ?", (user_id,))
    questions_created = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM exams WHERE user_id = ?", (user_id,))
    exams_created = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(DISTINCT exam_id) FROM exam_attempts WHERE user_id = ?", (user_id,))
    exams_attended = (await cursor.fetchone())[0]

    cursor = await db.execute(
        "SELECT AVG(CAST(score AS FLOAT) / NULLIF(total_marks, 0) * 100) FROM exam_attempts WHERE user_id = ? AND total_marks > 0",
        (user_id,),
    )
    accuracy_row = await cursor.fetchone()
    accuracy = float(accuracy_row[0]) if accuracy_row and accuracy_row[0] is not None else 0.0

    cursor = await db.execute(
        """
        SELECT rank FROM (
            SELECT l.user_id AS user_id, RANK() OVER (ORDER BY SUM(l.score) DESC, AVG(CAST(l.score AS FLOAT) / NULLIF(ea.total_marks, 0) * 100) DESC) AS rank
            FROM leaderboard l
            JOIN exam_attempts ea ON ea.id = l.attempt_id
            GROUP BY l.user_id
        ) ranked
        WHERE ranked.user_id = ?
        """,
        (user_id,),
    )
    rank_row = await cursor.fetchone()
    global_rank = int(rank_row[0]) if rank_row and rank_row[0] is not None else None

    cursor = await db.execute(
        "SELECT id, title, difficulty, created_at FROM questions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    )
    recent_questions = [
        {"id": row[0], "title": row[1], "difficulty": row[2], "created_at": row[3]}
        for row in await cursor.fetchall()
    ]

    cursor = await db.execute(
        "SELECT id, title, duration_minutes, total_marks, created_at FROM exams WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    )
    recent_exams = [
        {"id": row[0], "title": row[1], "duration_minutes": row[2], "total_marks": row[3], "created_at": row[4]}
        for row in await cursor.fetchall()
    ]

    profile = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "avatar_url": user["avatar_url"],
        "bio": user["bio"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "stats": {
            "global_rank": global_rank,
            "exams_attended": exams_attended,
            "exams_created": exams_created,
            "questions_created": questions_created,
            "accuracy": accuracy,
        },
        "recent_questions": recent_questions,
        "recent_exams": recent_exams,
    }
    return profile


async def get_user_bookmarks(db, user_id: int) -> list[dict]:
    cursor = await db.execute(
        """
        SELECT q.id, q.title, q.description, q.type, q.difficulty, q.likes_count, q.created_at
        FROM bookmarks b
        JOIN questions q ON q.id = b.question_id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
        """,
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "type": row[3],
            "difficulty": row[4],
            "likes_count": row[5],
            "created_at": row[6],
        }
        for row in rows
    ]


async def get_user_questions(db, user_id: int) -> list[dict]:
    cursor = await db.execute(
        "SELECT id, title, difficulty, created_at FROM questions WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "difficulty": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]


async def get_user_exams(db, user_id: int) -> list[dict]:
    cursor = await db.execute(
        "SELECT id, title, duration_minutes, total_marks, created_at FROM exams WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "duration_minutes": row[2],
            "total_marks": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]
