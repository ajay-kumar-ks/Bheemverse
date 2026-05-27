from typing import Any, Dict, List, Optional


def _row_to_question(row) -> Optional[dict]:
    if row is None:
        return None
    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "description": row[3],
        "type": row[4],
        "correct_answer": row[5],
        "difficulty": row[6],
        "explanation": row[7],
        "is_public": bool(row[8]),
        "likes_count": row[9],
        "created_at": row[10],
        "updated_at": row[11],
    }


async def _get_tags(db, question_id: int) -> List[dict]:
    cursor = await db.execute(
        "SELECT t.id, t.name FROM tags t JOIN question_tags qt ON qt.tag_id = t.id WHERE qt.question_id = ?",
        (question_id,),
    )
    rows = await cursor.fetchall()
    return [{"id": row[0], "name": row[1]} for row in rows]


async def _get_options(db, question_id: int) -> List[dict]:
    cursor = await db.execute(
        "SELECT id, option_text, option_order FROM question_options WHERE question_id = ? ORDER BY option_order",
        (question_id,),
    )
    rows = await cursor.fetchall()
    return [{"id": row[0], "option_text": row[1], "option_order": row[2]} for row in rows]


async def _get_or_create_tag_id(db, name: str) -> int:
    cursor = await db.execute("SELECT id FROM tags WHERE name = ?", (name,))
    row = await cursor.fetchone()
    if row:
        return row[0]
    cursor = await db.execute("INSERT INTO tags (name) VALUES (?)", (name,))
    await db.commit()
    return cursor.lastrowid


async def create_question(
    db,
    user_id: int,
    title: str,
    description: str | None,
    type: str,
    correct_answer: str | None,
    difficulty: str,
    explanation: str | None,
    is_public: bool,
    tag_names: list[str],
    options: list[dict[str, Any]],
) -> dict:
    cursor = await db.execute(
        "INSERT INTO questions (user_id, title, description, type, correct_answer, difficulty, explanation, is_public) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, title, description, type, correct_answer, difficulty, explanation, int(is_public)),
    )
    question_id = cursor.lastrowid
    await db.commit()

    for tag_name in tag_names:
        tag_id = await _get_or_create_tag_id(db, tag_name.strip())
        await db.execute(
            "INSERT OR IGNORE INTO question_tags (question_id, tag_id) VALUES (?, ?)",
            (question_id, tag_id),
        )

    for option in options:
        await db.execute(
            "INSERT INTO question_options (question_id, option_text, option_order) VALUES (?, ?, ?)",
            (question_id, option["option_text"], option["option_order"]),
        )

    await db.commit()
    return await get_question_by_id(db, question_id)


async def get_question_by_id(db, question_id: int) -> Optional[dict]:
    cursor = await db.execute(
        "SELECT id, user_id, title, description, type, correct_answer, difficulty, explanation, is_public, likes_count, created_at, updated_at FROM questions WHERE id = ?",
        (question_id,),
    )
    row = await cursor.fetchone()
    question = _row_to_question(row)
    if question is None:
        return None
    question["tags"] = await _get_tags(db, question_id)
    question["options"] = await _get_options(db, question_id)
    return question


async def list_questions(db, page: int = 1, limit: int = 20, only_public: bool = True) -> list[dict]:
    offset = (page - 1) * limit
    query = "SELECT id, user_id, title, description, type, correct_answer, difficulty, explanation, is_public, likes_count, created_at, updated_at FROM questions"
    params: list = []
    if only_public:
        query += " WHERE is_public = 1"
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    questions = [_row_to_question(row) for row in rows]
    for question in questions:
        question["tags"] = await _get_tags(db, question["id"])
        question["options"] = await _get_options(db, question["id"])
    return questions


async def update_question(
    db,
    question_id: int,
    title: str | None = None,
    description: str | None = None,
    type: str | None = None,
    correct_answer: str | None = None,
    difficulty: str | None = None,
    explanation: str | None = None,
    is_public: bool | None = None,
    tag_names: list[str] | None = None,
    options: list[dict[str, Any]] | None = None,
) -> Optional[dict]:
    current = await get_question_by_id(db, question_id)
    if current is None:
        return None
    fields = []
    values: list = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if description is not None:
        fields.append("description = ?")
        values.append(description)
    if type is not None:
        fields.append("type = ?")
        values.append(type)
    if correct_answer is not None:
        fields.append("correct_answer = ?")
        values.append(correct_answer)
    if difficulty is not None:
        fields.append("difficulty = ?")
        values.append(difficulty)
    if explanation is not None:
        fields.append("explanation = ?")
        values.append(explanation)
    if is_public is not None:
        fields.append("is_public = ?")
        values.append(int(is_public))
    if fields:
        values.append(question_id)
        await db.execute(f"UPDATE questions SET {', '.join(fields)}, updated_at = datetime('now') WHERE id = ?", tuple(values))

    if tag_names is not None:
        await db.execute("DELETE FROM question_tags WHERE question_id = ?", (question_id,))
        for tag_name in tag_names:
            tag_id = await _get_or_create_tag_id(db, tag_name.strip())
            await db.execute(
                "INSERT OR IGNORE INTO question_tags (question_id, tag_id) VALUES (?, ?)",
                (question_id, tag_id),
            )

    if options is not None:
        await db.execute("DELETE FROM question_options WHERE question_id = ?", (question_id,))
        for option in options:
            await db.execute(
                "INSERT INTO question_options (question_id, option_text, option_order) VALUES (?, ?, ?)",
                (question_id, option["option_text"], option["option_order"]),
            )

    await db.commit()
    return await get_question_by_id(db, question_id)


async def delete_question(db, question_id: int) -> None:
    await db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    await db.commit()


async def increment_like(db, question_id: int) -> Optional[dict]:
    await db.execute("UPDATE questions SET likes_count = likes_count + 1 WHERE id = ?", (question_id,))
    await db.commit()
    return await get_question_by_id(db, question_id)


async def toggle_bookmark(db, user_id: int, question_id: int) -> dict:
    cursor = await db.execute(
        "SELECT 1 FROM bookmarks WHERE user_id = ? AND question_id = ?",
        (user_id, question_id),
    )
    existing = await cursor.fetchone()
    if existing:
        await db.execute("DELETE FROM bookmarks WHERE user_id = ? AND question_id = ?", (user_id, question_id))
        await db.commit()
        return {"bookmarked": False}
    await db.execute("INSERT INTO bookmarks (user_id, question_id) VALUES (?, ?)", (user_id, question_id))
    await db.commit()
    return {"bookmarked": True}
