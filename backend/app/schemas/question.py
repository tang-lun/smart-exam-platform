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
    created_at: datetime

    model_config = {"from_attributes": True}


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
