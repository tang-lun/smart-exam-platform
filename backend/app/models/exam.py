from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_ids: Mapped[list] = mapped_column(JSON, default=list)
    question_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    total_score: Mapped[int] = mapped_column(Integer, default=100)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
