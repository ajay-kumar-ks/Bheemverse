from typing import List, Optional

from pydantic import BaseModel, Field, constr, validator


class QuestionOption(BaseModel):
    option_text: str = Field(..., min_length=1)
    option_order: int = Field(..., ge=1)


class QuestionCreate(BaseModel):
    title: constr(min_length=5, max_length=255)
    description: Optional[str] = None
    type: str = Field(..., pattern='^(mcq|true_false|short_answer|descriptive)$')
    correct_answer: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern='^(easy|medium|hard)$')
    explanation: Optional[str] = None
    is_public: Optional[bool] = True
    tags: Optional[List[constr(min_length=1, max_length=50)]] = []
    options: Optional[List[QuestionOption]] = []

    @validator('options', always=True)
    def validate_options(cls, value, values):
        if values.get('type') == 'mcq' and (not value or len(value) < 2):
            raise ValueError('MCQ questions require at least two options')
        return value


class QuestionUpdate(BaseModel):
    title: Optional[constr(min_length=5, max_length=255)] = None
    description: Optional[str] = None
    type: Optional[str] = Field(None, pattern='^(mcq|true_false|short_answer|descriptive)$')
    correct_answer: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern='^(easy|medium|hard)$')
    explanation: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[constr(min_length=1, max_length=50)]] = None
    options: Optional[List[QuestionOption]] = None


class TagOut(BaseModel):
    id: int
    name: str


class QuestionOptionOut(BaseModel):
    id: int
    option_text: str
    option_order: int


class QuestionOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    type: str
    correct_answer: Optional[str] = None
    difficulty: str
    explanation: Optional[str] = None
    is_public: bool
    likes_count: int
    tags: List[TagOut] = []
    options: List[QuestionOptionOut] = []
    created_at: str
    updated_at: str


class CommentCreate(BaseModel):
    content: constr(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    id: int
    question_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    is_flagged: bool
    created_at: str
    replies: List['CommentOut'] = []


CommentOut.update_forward_refs()
