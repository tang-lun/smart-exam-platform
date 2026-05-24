import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class QuestionType(str, enum.Enum):
    choice = "choice"
    fill_blank = "fill_blank"
    calculation = "calculation"
    proof = "proof"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionSource(str, enum.Enum):
    ai_generated = "ai_generated"
    manual = "manual"
    imported = "imported"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    subject: Mapped[str] = mapped_column(String(32), default="math")
    grade_level: Mapped[str] = mapped_column(String(32), default="grade_7")
    knowledge_points: Mapped[list] = mapped_column(JSON, default=list)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.medium)
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    answer_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[QuestionSource] = mapped_column(Enum(QuestionSource), default=QuestionSource.ai_generated)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    favorited_by: Mapped[list] = mapped_column(JSON, default=list, comment="收藏该题目的用户ID列表")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
