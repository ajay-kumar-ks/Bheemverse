from typing import Dict, List, Optional

from pydantic import BaseModel, Field, FieldValidationInfo, constr, model_validator


class ExamQuestionCreate(BaseModel):
    question_id: int
    marks: int = Field(..., ge=1)
    question_order: Optional[int] = None


class ExamCreate(BaseModel):
    title: constr(min_length=5, max_length=255)
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=5)
    total_marks: int = Field(..., ge=1)
    is_public: Optional[bool] = True
    randomize_order: Optional[bool] = False
    questions: List[ExamQuestionCreate] = Field(..., min_items=1)


class ExamUpdate(BaseModel):
    title: Optional[constr(min_length=5, max_length=255)] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=5)
    total_marks: Optional[int] = Field(None, ge=1)
    is_public: Optional[bool] = None
    randomize_order: Optional[bool] = None
    questions: Optional[List[ExamQuestionCreate]] = None


class ExamQuestionOut(BaseModel):
    question_id: int
    title: str
    type: str
    difficulty: str
    marks: int
    question_order: int


class ExamOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: int
    is_public: bool
    randomize_order: bool
    questions: List[ExamQuestionOut] = []
    created_at: str
    updated_at: str


class AttemptStart(BaseModel):
    id: int
    exam_id: int
    user_id: int
    attempt_number: int
    total_marks: int


class AttemptSubmit(BaseModel):
    attempt_id: int
    time_taken_seconds: int = Field(..., ge=0)
    answers: Dict[int, str]

    @model_validator(mode="after")
    def ensure_answers_present(self):
        if not self.answers:
            raise ValueError("Answers payload cannot be empty")
        return self


class ResultOut(BaseModel):
    id: int
    exam_id: int
    user_id: int
    attempt_number: int
    score: int
    total_marks: int
    time_taken_seconds: int
    answers: Dict[str, str]
    submitted_at: str
