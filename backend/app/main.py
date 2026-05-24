from datetime import datetime, timezone

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import auth, exams, questions
from app.config import settings
from app.db.database import Base, engine, get_db
from app.models.exam import Exam
from app.models.question import Question, QuestionSource
from app.models.user import User
from app.services.auth_service import get_current_user

Base.metadata.create_all(bind=engine)


def _auto_migrate():
    """自动补全/清理数据库列，避免旧数据库与模型不一致导致 500 错误。"""
    import sqlite3
    import re
    db_url = settings.database_url
    match = re.match(r"sqlite:///(.+)", db_url)
    if not match:
        return
    db_path = match.group(1)
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # questions 表 — 新增列
        cols = {r[1] for r in cur.execute("PRAGMA table_info(questions)")}
        if "favorited_by" not in cols:
            cur.execute("ALTER TABLE questions ADD COLUMN favorited_by TEXT DEFAULT '[]'")
        if "updated_at" not in cols:
            cur.execute("ALTER TABLE questions ADD COLUMN updated_at DATETIME")
        # 清理旧版本遗留的 is_favorited 列（已被 favorited_by 取代，NOT NULL 约束会阻止插入）
        if "is_favorited" in cols:
            cur.execute("ALTER TABLE questions DROP COLUMN is_favorited")
        conn.commit()
        conn.close()
    except Exception:
        pass  # 数据库文件还不存在时跳过


_auto_migrate()

app = FastAPI(title="智能题库与试卷生成平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(exams.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_questions = db.query(func.count(Question.id)).filter(
        Question.owner_id == current_user.id
    ).scalar()
    ai_generated = db.query(func.count(Question.id)).filter(
        Question.source == QuestionSource.ai_generated,
        Question.owner_id == current_user.id,
    ).scalar()
    total_exams = db.query(func.count(Exam.id)).filter(
        Exam.owner_id == current_user.id
    ).scalar()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_new = db.query(func.count(Question.id)).filter(
        Question.created_at >= today,
        Question.owner_id == current_user.id,
    ).scalar()
    return {
        "total_questions": total_questions,
        "ai_generated": ai_generated,
        "total_exams": total_exams,
        "today_new": today_new,
    }
