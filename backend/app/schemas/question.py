from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class QuestionGenerateRequest(BaseModel):
    knowledge_points: list[str] = Field(..., min_length=1, description="知识点列表，如 ['一元一次方程']")
    question_type: str = Field(default="choice", description="题型: choice / fill_blank / calculation / proof")
    count: int = Field(default=5, ge=1, le=10, description="生成数量")
    difficulty: str = Field(default="medium", description="难度: easy / medium / hard")
    grade_level: str = Field(default="grade_7", description="学段: grade_7 / grade_8 / grade_9")

    @model_validator(mode="after")
    def validate_count_by_type(self):
        if self.question_type == "proof" and self.count > 3:
            raise ValueError("证明题单次最多生成 3 道，请分次生成")
        if self.question_type == "calculation" and self.count > 5:
            raise ValueError("计算题单次最多生成 5 道，请分次生成")
        return self


class QuestionResponse(BaseModel):
    id: int
    type: str
    subject: str
    grade_level: str
    knowledge_points: list
    difficulty: str
    stem: str
    options: list | None = None
    answer: str
    answer_analysis: str | None = None
    source: str
    is_favorited: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_question(cls, q, user_id: int | None = None):
        """从 ORM 对象构建响应，自动计算当前用户的收藏状态。"""
        return cls(
            id=q.id,
            type=q.type.value if hasattr(q.type, 'value') else str(q.type),
            subject=q.subject,
            grade_level=q.grade_level,
            knowledge_points=q.knowledge_points or [],
            difficulty=q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
            stem=q.stem,
            options=q.options,
            answer=q.answer,
            answer_analysis=q.answer_analysis,
            source=q.source.value if hasattr(q.source, 'value') else str(q.source),
            is_favorited=(user_id in (q.favorited_by or [])) if user_id else False,
            created_at=q.created_at,
        )


class QuestionManualCreate(BaseModel):
    type: str = Field(..., description="题型: choice / fill_blank / calculation / proof")
    grade_level: str = Field(default="grade_7")
    knowledge_points: list[str] = Field(..., min_length=1)
    difficulty: str = Field(default="medium")
    stem: str = Field(..., min_length=1, description="题干")
    options: list[str] | None = Field(None, description="选项列表（选择题必填）")
    answer: str = Field(..., min_length=1)
    answer_analysis: str | None = None


class QuestionUpdateRequest(BaseModel):
    type: str | None = None
    grade_level: str | None = None
    knowledge_points: list | None = None
    difficulty: str | None = None
    stem: str | None = None
    options: list | None = None
    answer: str | None = None
    answer_analysis: str | None = None


class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    page_size: int
