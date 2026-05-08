from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.question import Question, QuestionSource
from app.schemas.question import (
    QuestionGenerateRequest,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdateRequest,
)
from app.services.ai_service import generate_questions

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("/generate", response_model=list[QuestionResponse], status_code=201)
def generate(req: QuestionGenerateRequest, db: Session = Depends(get_db)):
    """AI 生成题目并存入题库。"""
    raw_questions = generate_questions(
        knowledge_points=req.knowledge_points,
        question_type=req.question_type,
        count=req.count,
        difficulty=req.difficulty,
        grade_level=req.grade_level,
    )

    created = []
    for q in raw_questions:
        question = Question(
            type=q.get("type", req.question_type),
            subject="math",
            grade_level=req.grade_level,
            knowledge_points=q.get("knowledge_points", req.knowledge_points),
            difficulty=q.get("difficulty", req.difficulty),
            stem=q["stem"],
            options=q.get("options"),
            answer=q["answer"],
            answer_analysis=q.get("answer_analysis"),
            source=QuestionSource.ai_generated,
        )
        db.add(question)
        created.append(question)

    db.commit()
    for q in created:
        db.refresh(q)

    return created


@router.get("", response_model=QuestionListResponse)
def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query("", description="搜索题干关键词"),
    question_type: str = Query("", description="按题型筛选"),
    difficulty: str = Query("", description="按难度筛选"),
    knowledge_point: str = Query("", description="按知识点筛选"),
    db: Session = Depends(get_db),
):
    """题目列表，支持搜索和筛选。"""
    query = db.query(Question)

    if keyword:
        query = query.filter(Question.stem.contains(keyword))
    if question_type:
        query = query.filter(Question.type == question_type)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    total = query.count()
    items = query.order_by(Question.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 知识点筛选在 DB 查询后做内存过滤（JSON 字段）
    if knowledge_point:
        items = [q for q in items if knowledge_point in q.knowledge_points]
        total = len(items)

    return QuestionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """获取单道题目详情。"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, req: QuestionUpdateRequest, db: Session = Depends(get_db)):
    """编辑题目。"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)
    return question


@router.delete("/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """删除题目。"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(question)
    db.commit()
