from typing import Any

try:
    from backend.models import question_model, comment_model
    from backend.services import ai_service, notification_service
except ImportError:
    from models import question_model, comment_model
    from services import ai_service, notification_service


async def create_question(
    db,
    user_id: int,
    title: str,
    description: str | None,
    type: str,
    correct_answer: str | None,
    difficulty: str | None,
    explanation: str | None,
    is_public: bool,
    tags: list[str] | None,
    options: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    tags = tags or []
    options = options or []

    duplicate_result = await ai_service.check_duplicate(db, title, description)
    if not tags:
        tags = await ai_service.suggest_tags(db, title, description)
    if not difficulty:
        difficulty_result = await ai_service.analyze_difficulty(db, title, description)
        difficulty = difficulty_result['difficulty']
    question = await question_model.create_question(
        db,
        user_id=user_id,
        title=title,
        description=description,
        type=type,
        correct_answer=correct_answer,
        difficulty=difficulty,
        explanation=explanation,
        is_public=is_public,
        tag_names=tags,
        options=options,
    )

    if question['is_public']:
        message = f"New public question created: {title}"
        await notification_service.create_notification(db, user_id, 'question_created', message, question['id'], 'question')

    question['duplicate_warning'] = duplicate_result if duplicate_result['is_duplicate'] else None
    return question


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
    tags: list[str] | None = None,
    options: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    return await question_model.update_question(
        db,
        question_id,
        title=title,
        description=description,
        type=type,
        correct_answer=correct_answer,
        difficulty=difficulty,
        explanation=explanation,
        is_public=is_public,
        tag_names=tags,
        options=options,
    )


async def get_question(db, question_id: int) -> dict[str, Any] | None:
    return await question_model.get_question_by_id(db, question_id)


async def list_questions(db, page: int = 1, limit: int = 20) -> list[dict[str, Any]]:
    return await question_model.list_questions(db, page=page, limit=limit, only_public=True)


async def delete_question(db, question_id: int) -> None:
    await question_model.delete_question(db, question_id)


async def like_question(db, question_id: int) -> dict[str, Any] | None:
    return await question_model.increment_like(db, question_id)


async def toggle_bookmark(db, user_id: int, question_id: int) -> dict[str, Any]:
    return await question_model.toggle_bookmark(db, user_id, question_id)


async def create_comment(db, question_id: int, user_id: int, content: str, parent_id: int | None = None) -> dict[str, Any]:
    comment = await comment_model.create_comment(db, question_id, user_id, content, parent_id)
    if parent_id is not None:
        cursor = await db.execute("SELECT user_id FROM comments WHERE id = ?", (parent_id,))
        row = await cursor.fetchone()
        if row and row[0] != user_id:
            message = "Someone replied to your comment."
            await notification_service.create_notification(db, row[0], 'comment_reply', message, comment['id'], 'comment')
    else:
        cursor = await db.execute("SELECT user_id FROM questions WHERE id = ?", (question_id,))
        row = await cursor.fetchone()
        if row and row[0] != user_id:
            message = "Someone commented on your question."
            await notification_service.create_notification(db, row[0], 'question_comment', message, comment['id'], 'comment')
    return comment


async def list_comments(db, question_id: int) -> list[dict[str, Any]]:
    return await comment_model.get_comments_by_question(db, question_id)
