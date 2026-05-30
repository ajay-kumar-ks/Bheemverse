from typing import List
from ..database import get_db
from .notification_service import create_notification

async def check_milestones(user_id: int):
    """
    Checks user statistics and grants badges if milestones are reached.
    Should be called after exam submissions or question creation.
    """
    async with get_db() as db:
        # 1. Fetch user stats
        stats_query = """
            SELECT 
                (SELECT COUNT(*) FROM exam_attempts WHERE user_id = ?) as exam_count,
                (SELECT COUNT(*) FROM questions WHERE user_id = ?) as question_count,
                (SELECT MAX(score) FROM exam_attempts WHERE user_id = ?) as max_score
        """
        async with db.execute(stats_query, (user_id, user_id, user_id)) as cursor:
            row = await cursor.fetchone()
            exam_count, question_count, max_score = row if row else (0, 0, 0)

        # 2. Fetch available badges the user doesn't have yet
        badges_query = """
            SELECT id, name, criteria_type, criteria_value 
            FROM badges 
            WHERE id NOT IN (SELECT badge_id FROM user_badges WHERE user_id = ?)
        """
        async with db.execute(badges_query, (user_id,)) as cursor:
            available_badges = await cursor.fetchall()

        # 3. Logic to unlock badges
        for badge_id, name, c_type, c_value in available_badges:
            unlocked = False
            if c_type == 'exams_completed' and exam_count >= c_value:
                unlocked = True
            elif c_type == 'questions_created' and question_count >= c_value:
                unlocked = True
            elif c_type == 'score_threshold' and max_score >= c_value:
                unlocked = True

            if unlocked:
                await db.execute(
                    "INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)",
                    (user_id, badge_id)
                )
                await create_notification(
                    user_id=user_id,
                    type="achievement_unlocked",
                    message=f"Congratulations! You've earned the '{name}' badge.",
                    reference_id=badge_id,
                    reference_type="badge"
                )
        await db.commit()