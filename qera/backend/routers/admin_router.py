from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from backend.services import ai_service
    from backend.middlewares.auth import get_current_user
    from backend.middlewares.role import require_admin
except ImportError:
    from services import ai_service
    from middlewares.auth import get_current_user
    from middlewares.role import require_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users")
async def list_users(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, name, email, role, is_suspended, avatar_url, bio, created_at, updated_at FROM users ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "is_suspended": bool(row[4]),
            "avatar_url": row[5],
            "bio": row[6],
            "created_at": row[7],
            "updated_at": row[8],
        }
        for row in rows
    ]


@router.put("/users/{user_id}/suspend")
async def suspend_user(request: Request, user_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute("UPDATE users SET is_suspended = 1 WHERE id = ?", (user_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User suspended"}


@router.put("/users/{user_id}/unsuspend")
async def unsuspend_user(request: Request, user_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute("UPDATE users SET is_suspended = 0 WHERE id = ?", (user_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User unsuspended"}


@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    user = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if await user.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    await db.commit()
    return {"message": "User removed successfully"}


@router.get("/questions/flagged")
async def list_flagged_questions(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, user_id, title, description, type, difficulty, is_public, is_flagged, created_at FROM questions WHERE is_flagged = 1 ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "description": row[3],
            "type": row[4],
            "difficulty": row[5],
            "is_public": bool(row[6]),
            "is_flagged": bool(row[7]),
            "created_at": row[8],
        }
        for row in rows
    ]


@router.put("/comments/{comment_id}/unflag")
async def unflag_comment(request: Request, comment_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute("UPDATE comments SET is_flagged = 0 WHERE id = ?", (comment_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return {"message": "Comment unflagged"}


@router.post("/comments/{comment_id}/flag")
async def flag_comment_admin(request: Request, comment_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    try:
        await db.execute("UPDATE comments SET is_flagged = 1 WHERE id = ?", (comment_id,))
        await db.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to flag comment")
    return {"message": "Comment flagged"}


@router.delete("/comments/{comment_id}")
async def delete_comment(request: Request, comment_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return {"message": "Comment deleted"}


@router.delete("/questions/{question_id}")
async def delete_question(request: Request, question_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return {"message": "Question deleted"}


@router.get("/exams")
async def list_exams(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, user_id, title, description, duration_minutes, total_marks, is_public, randomize_order, created_at, updated_at FROM exams ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "description": row[3],
            "duration_minutes": row[4],
            "total_marks": row[5],
            "is_public": bool(row[6]),
            "randomize_order": bool(row[7]),
            "created_at": row[8],
            "updated_at": row[9],
        }
        for row in rows
    ]


@router.post("/moderate/batch")
async def moderate_batch(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    flagged = []

    comment_cursor = await db.execute("SELECT id, content FROM comments WHERE is_flagged = 0 ORDER BY created_at ASC")
    comment_rows = await comment_cursor.fetchall()
    for row in comment_rows:
        comment_id, content = row[0], row[1]
        verdict = await ai_service.moderation_filter(content)
        if verdict.get("is_toxic") or verdict.get("is_spam"):
            await db.execute("UPDATE comments SET is_flagged = 1 WHERE id = ?", (comment_id,))
            flagged.append({"type": "comment", "id": comment_id, "reason": verdict.get("reason")})

    question_cursor = await db.execute("SELECT id, title, description FROM questions WHERE is_flagged = 0 ORDER BY created_at ASC")
    question_rows = await question_cursor.fetchall()
    for row in question_rows:
        question_id, title, description = row[0], row[1], row[2]
        text = f"{title} {description or ''}".strip()
        verdict = await ai_service.moderation_filter(text)
        if verdict.get("is_toxic") or verdict.get("is_spam"):
            await db.execute("UPDATE questions SET is_flagged = 1 WHERE id = ?", (question_id,))
            flagged.append({"type": "question", "id": question_id, "reason": verdict.get("reason")})

    await db.commit()
    return {"flagged_count": len(flagged), "flagged_items": flagged}
