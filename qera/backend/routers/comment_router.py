from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from backend.schemas.question_schema import CommentCreate, CommentOut
    from backend.services.question_service import create_comment, list_comments, get_question
    from backend.middlewares.auth import get_current_user
except ImportError:
    from schemas.question_schema import CommentCreate, CommentOut
    from services.question_service import create_comment, list_comments, get_question
    from middlewares.auth import get_current_user

router = APIRouter(prefix="/api/v1/questions", tags=["comments"])


@router.get("/{question_id}/comments", response_model=list[CommentOut])
async def read_comments(request: Request, question_id: int):
    db = request.app.state.db
    question = await get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return await list_comments(db, question_id)


@router.post("/{question_id}/comments", response_model=CommentOut)
async def create_question_comment(request: Request, question_id: int, payload: CommentCreate, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    question = await get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return await create_comment(db, question_id, current_user["id"], payload.content)


@router.post("/{question_id}/comments/{comment_id}/reply", response_model=CommentOut)
async def reply_to_comment(request: Request, question_id: int, comment_id: int, payload: CommentCreate, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    question = await get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return await create_comment(db, question_id, current_user["id"], payload.content, parent_id=comment_id)
