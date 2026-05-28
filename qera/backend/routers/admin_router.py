from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from backend.middlewares.auth import get_current_user
    from backend.middlewares.role import require_admin
except ImportError:
    from middlewares.auth import get_current_user
    from middlewares.role import require_admin

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users")
async def list_users(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, name, email, role, avatar_url, bio, created_at, updated_at FROM users ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "avatar_url": row[4],
            "bio": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }
        for row in rows
    ]


@router.delete("/users/{user_id}")
async def delete_user(request: Request, user_id: int, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    user = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if await user.fetchone() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    await db.commit()
    return {"message": "User removed successfully"}


@router.get("/comments/flagged")
async def list_flagged_comments(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, question_id, user_id, parent_id, content, is_flagged, created_at FROM comments WHERE is_flagged = 1 ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "question_id": row[1],
            "user_id": row[2],
            "parent_id": row[3],
            "content": row[4],
            "is_flagged": bool(row[5]),
            "created_at": row[6],
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


@router.post("/moderate/batch")
async def moderate_batch(request: Request, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    cursor = await db.execute(
        "SELECT id, content FROM comments WHERE is_flagged = 0 ORDER BY created_at ASC"
    )
    rows = await cursor.fetchall()
    flagged = []
    for row in rows:
        comment_id, content = row[0], row[1]
        normalized = content.lower()
        if any(term in normalized for term in ["spam", "abuse", "offensive", "hate", "cheat"]):
            await db.execute("UPDATE comments SET is_flagged = 1 WHERE id = ?", (comment_id,))
            flagged.append(comment_id)
    await db.commit()
    return {"flagged_count": len(flagged), "flagged_ids": flagged}
