from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.question import QuestionResponse


class ExamCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    question_ids: list[int] = Field(default=[], description="手动选题时的题目ID列表")
    total_score: int = Field(default=150)
    duration_minutes: int = Field(default=120)
    # AI 组卷参数（当 question_ids 为空时使用）
    knowledge_points: list[str] = Field(default=[], description="知识点范围")
    difficulty_distribution: dict[str, int] = Field(
        default={"easy": 30, "medium": 40, "hard": 30},
        description="难度百分比分布"
    )
    type_distribution: dict[str, int] = Field(
        default={"choice": 12, "fill_blank": 4, "calculation": 3, "proof": 3},
        description="题型数量分布"
    )
    grade_levels: list[str] = Field(default=[], description="学段筛选，如 ['grade_7', 'grade_8']，空则不限")
    question_count: int = Field(default=10, description="AI 组卷时的题目总数")


class ExamResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    question_ids: list[int]
    question_scores: dict = {}
    total_score: int
    duration_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ExamDetailResponse(ExamResponse):
    questions: list[QuestionResponse] = []


class ExamListResponse(BaseModel):
    items: list[ExamResponse]
    total: int


class ExamSubmitRequest(BaseModel):
    answers: dict[int, str] = Field(default={}, description="用户答案，key为题号索引，value为答案")
    started_at: str | None = Field(default=None, description="客户端考试开始时间 ISO 格式，用于服务端超时校验")


class ExamResultResponse(BaseModel):
    id: int
    exam_id: int
    score: int
    total_score: int
    correct_count: int
    total_count: int
    answers: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class ExamResultListResponse(BaseModel):
    items: list[ExamResultResponse]
    total: int
