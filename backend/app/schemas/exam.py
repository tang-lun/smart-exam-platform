from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.question import QuestionResponse


class ExamCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    question_ids: list[int] = Field(default=[], description="手动选题时的题目ID列表")
    total_score: int = Field(default=100)
    duration_minutes: int = Field(default=60)
    # AI 组卷参数（当 question_ids 为空时使用）
    knowledge_points: list[str] = Field(default=[], description="知识点范围")
    difficulty_distribution: dict[str, int] = Field(
        default={"easy": 30, "medium": 50, "hard": 20},
        description="难度百分比分布"
    )
    question_count: int = Field(default=10, description="AI 组卷时的题目总数")


class ExamResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    question_ids: list[int]
    total_score: int
    duration_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ExamDetailResponse(ExamResponse):
    questions: list[QuestionResponse] = []


class ExamListResponse(BaseModel):
    items: list[ExamResponse]
    total: int
