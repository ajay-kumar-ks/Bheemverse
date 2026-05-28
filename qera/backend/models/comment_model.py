from typing import Optional


def _row_to_comment(row) -> dict:
    return {
        "id": row[0],
        "question_id": row[1],
        "user_id": row[2],
        "parent_id": row[3],
        "content": row[4],
        "is_flagged": bool(row[5]),
        "created_at": row[6],
        "replies": [],
    }


async def create_comment(db, question_id: int, user_id: int, content: str, parent_id: int | None = None) -> dict:
    cursor = await db.execute(
        "INSERT INTO comments (question_id, user_id, parent_id, content) VALUES (?, ?, ?, ?)",
        (question_id, user_id, parent_id, content),
    )
    await db.commit()
    comment_id = cursor.lastrowid
    cursor = await db.execute(
        "SELECT id, question_id, user_id, parent_id, content, is_flagged, created_at FROM comments WHERE id = ?",
        (comment_id,),
    )
    row = await cursor.fetchone()
    return _row_to_comment(row)


async def get_comments_by_question(db, question_id: int, include_flagged: bool = False) -> list[dict]:
    query = "SELECT id, question_id, user_id, parent_id, content, is_flagged, created_at FROM comments WHERE question_id = ?"
    params = [question_id]
    if not include_flagged:
        query += " AND is_flagged = 0"
    query += " ORDER BY created_at ASC"
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    comments = [_row_to_comment(row) for row in rows]
    return _nest_comments(comments)


async def flag_comment(db, comment_id: int) -> dict | None:
    """Set is_flagged=1 for a comment and return the updated comment, or None if not found."""
    await db.execute("UPDATE comments SET is_flagged = 1 WHERE id = ?", (comment_id,))
    await db.commit()
    cursor = await db.execute(
        "SELECT id, question_id, user_id, parent_id, content, is_flagged, created_at FROM comments WHERE id = ?",
        (comment_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_comment(row)


def _nest_comments(flat_comments: list[dict]) -> list[dict]:
    comments_by_id = {comment["id"]: comment for comment in flat_comments}
    root_comments = []
    for comment in flat_comments:
        if comment["parent_id"] and comment["parent_id"] in comments_by_id:
            comments_by_id[comment["parent_id"]]["replies"].append(comment)
        else:
            root_comments.append(comment)
    return root_comments
