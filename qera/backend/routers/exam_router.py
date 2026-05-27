from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from backend.schemas.exam_schema import ExamCreate, ExamOut, ExamUpdate, AttemptStart, AttemptSubmit, ResultOut
    from backend.services.exam_service import start_exam_attempt, submit_exam_attempt, notify_new_exam
    from backend.models import exam_model
    from backend.middlewares.auth import get_current_user
    from backend.middlewares.role import require_admin
except ImportError:
    from schemas.exam_schema import ExamCreate, ExamOut, ExamUpdate, AttemptStart, AttemptSubmit, ResultOut
    from services.exam_service import start_exam_attempt, submit_exam_attempt, notify_new_exam
    from models import exam_model
    from middlewares.auth import get_current_user
    from middlewares.role import require_admin

router = APIRouter(prefix="/api/v1/exams", tags=["exams"])


@router.get("/", response_model=list[ExamOut])
async def read_exams(request: Request, page: int = 1, limit: int = 20):
    db = request.app.state.db
    return await exam_model.list_exams(db, page=page, limit=limit)


@router.get("/{exam_id}", response_model=ExamOut)
async def read_exam(request: Request, exam_id: int):
    db = request.app.state.db
    exam = await exam_model.get_exam_by_id(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam


@router.post("/", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
async def create_exam(request: Request, payload: ExamCreate, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    exam = await exam_model.create_exam(
        db,
        user_id=current_user["id"],
        title=payload.title,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        total_marks=payload.total_marks,
        is_public=payload.is_public,
        randomize_order=payload.randomize_order,
        questions=[question.model_dump() for question in payload.questions],
    )
    await notify_new_exam(db, exam)
    return exam


@router.put("/{exam_id}", response_model=ExamOut)
async def update_exam(request: Request, exam_id: int, payload: ExamUpdate, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    exam = await exam_model.get_exam_by_id(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    if current_user["role"] != "admin" and exam["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this exam")
    updated = await exam_model.update_exam(
        db,
        exam_id,
        title=payload.title,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        total_marks=payload.total_marks,
        is_public=payload.is_public,
        randomize_order=payload.randomize_order,
        questions=[question.model_dump() for question in payload.questions] if payload.questions is not None else None,
    )
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return updated


@router.delete("/{exam_id}")
async def delete_exam(request: Request, exam_id: int, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    exam = await exam_model.get_exam_by_id(db, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    if current_user["role"] != "admin" and exam["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this exam")
    await exam_model.delete_exam(db, exam_id)
    return {"message": "Exam deleted successfully"}


@router.post("/{exam_id}/start", response_model=AttemptStart)
async def start_exam(request: Request, exam_id: int, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    return await start_exam_attempt(db, exam_id, current_user["id"])


@router.post("/{exam_id}/submit", response_model=ResultOut)
async def submit_exam(request: Request, exam_id: int, payload: AttemptSubmit, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    attempt = await exam_model.get_attempt(db, payload.attempt_id)
    if attempt is None or attempt["exam_id"] != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return await submit_exam_attempt(db, payload.attempt_id, current_user["id"], payload.time_taken_seconds, payload.answers)


@router.get("/{exam_id}/result/{attempt_id}", response_model=ResultOut)
async def read_exam_result(request: Request, exam_id: int, attempt_id: int, current_user: dict = Depends(get_current_user)):
    db = request.app.state.db
    attempt = await exam_model.get_attempt(db, attempt_id)
    if attempt is None or attempt["exam_id"] != exam_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if current_user["role"] != "admin" and attempt["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this attempt")
    return attempt


@router.post("/generate", response_model=ExamOut)
async def generate_exam(request: Request, payload: ExamCreate, current_user: dict = Depends(get_current_user), _: dict = Depends(require_admin)):
    db = request.app.state.db
    exam = await exam_model.create_exam(
        db,
        user_id=current_user["id"],
        title=payload.title,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        total_marks=payload.total_marks,
        is_public=payload.is_public,
        randomize_order=payload.randomize_order,
        questions=[question.model_dump() for question in payload.questions],
    )
    await notify_new_exam(db, exam)
    return exam
