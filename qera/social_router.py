from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db
from ..middlewares.auth import get_current_user
from typing import List, Optional

router = APIRouter(prefix="/api/v1/social", tags=["social"])

@router.post("/comments/{comment_id}/upvote")
async def upvote_comment(comment_id: int, current_user = Depends(get_current_user)):
    async with get_db() as db:
        # Check for existing vote
        async with db.execute(
            "SELECT 1 FROM comment_votes WHERE user_id = ? AND comment_id = ?",
            (current_user["id"], comment_id)
        ) as cursor:
            if await cursor.fetchone():
                raise HTTPException(status_code=400, detail="Already upvoted this comment")

        # Atomic increment and record vote
        await db.execute(
            "INSERT INTO comment_votes (user_id, comment_id) VALUES (?, ?)",
            (current_user["id"], comment_id)
        )
        await db.execute(
            "UPDATE comments SET upvotes_count = upvotes_count + 1 WHERE id = ?",
            (comment_id,)
        )
        await db.commit()
    return {"status": "success", "message": "Comment upvoted"}

@router.put("/comments/{comment_id}/helpful")
async def mark_helpful(comment_id: int, current_user = Depends(get_current_user)):
    async with get_db() as db:
        # Permission check: Only the question author can mark as helpful
        async with db.execute(
            "SELECT question_id FROM comments WHERE id = ?", (comment_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Comment not found")
            question_id = row[0]

        # Verify if current user is the author of the question
        async with db.execute(
            "SELECT user_id FROM questions WHERE id = ?", (question_id,)
        ) as cursor:
            q_row = await cursor.fetchone()
            if not q_row or q_row[0] != current_user["id"]:
                raise HTTPException(status_code=403, detail="Only the question author can mark helpful replies")

        await db.execute("UPDATE comments SET is_helpful = 1 WHERE id = ?", (comment_id,))
        await db.commit()
    return {"status": "success", "message": "Comment marked as helpful"}

@router.get("/badges/{user_id}")
async def get_user_badges(user_id: int):
    async with get_db() as db:
        query = """
            SELECT b.id, b.name, b.description, b.icon_url, ub.unlocked_at 
            FROM badges b
            JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id = ?
            ORDER BY ub.unlocked_at DESC
        """
        async with db.execute(query, (user_id,)) as cursor:
            badges = await cursor.fetchall()
            return [{"id": r[0], "name": r[1], "description": r[2], "icon_url": r[3], "unlocked_at": r[4]} for r in badges]

@router.get("/activity-feed")
async def get_activity_feed(current_user = Depends(get_current_user)):
    """Retrieve the 20 most recent notifications for the activity feed."""
    async with get_db() as db:
        query = """
            SELECT type, message, created_at, reference_id, reference_type 
            FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC LIMIT 20
        """
        async with db.execute(query, (current_user["id"],)) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "type": r[0], 
                    "message": r[1], 
                    "created_at": r[2], 
                    "reference_id": r[3], 
                    "reference_type": r[4]
                } for r in rows
            ]

@router.put("/notifications/read-all")
async def mark_all_notifications_read(current_user = Depends(get_current_user)):
    """Mark all unread notifications as read for the current user."""
    async with get_db() as db:
        await db.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
            (current_user["id"],)
        )
        await db.commit()
    return {"status": "success", "message": "All notifications marked as read"}

@router.get("/questions/{question_id}/comments")
async def get_sorted_comments(question_id: int, sort_by: str = "newest"):
    """Fetch comments for a question with sorting: 'newest' or 'helpful'."""
    order_clause = "created_at DESC" if sort_by == "newest" else "upvotes_count DESC, is_helpful DESC"
    async with get_db() as db:
        query = f"""
            SELECT c.id, c.content, c.user_id, c.created_at, c.upvotes_count, c.is_helpful, u.name as author_name 
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.question_id = ? AND c.is_flagged = 0
            ORDER BY {order_clause}
        """
        async with db.execute(query, (question_id,)) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "id": r[0], "content": r[1], "user_id": r[2], "created_at": r[3],
                    "upvotes_count": r[4], "is_helpful": r[5], "author_name": r[6]
                } for r in rows
            ]