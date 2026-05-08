from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.exam import Exam
from app.models.question import Question
from app.schemas.exam import (
    ExamCreateRequest,
    ExamDetailResponse,
    ExamListResponse,
    ExamResponse,
)
from app.schemas.question import QuestionResponse
from app.services.exam_service import auto_select_questions

router = APIRouter(prefix="/api/exams", tags=["exams"])


@router.post("", response_model=ExamDetailResponse, status_code=201)
def create_exam(req: ExamCreateRequest, db: Session = Depends(get_db)):
    """创建试卷（支持手动选题或 AI 自动组卷）。"""
    if req.question_ids:
        # 手动选题
        questions = db.query(Question).filter(Question.id.in_(req.question_ids)).all()
        if len(questions) != len(req.question_ids):
            raise HTTPException(status_code=400, detail="部分题目不存在")
        question_ids = req.question_ids
    else:
        # AI 自动组卷
        selected = auto_select_questions(
            db=db,
            knowledge_points=req.knowledge_points,
            question_count=req.question_count,
            difficulty_distribution=req.difficulty_distribution,
        )
        if not selected:
            raise HTTPException(status_code=400, detail="题库中没有符合条件的题目，请先生成题目")
        question_ids = [q.id for q in selected]

    exam = Exam(
        title=req.title,
        description=req.description,
        question_ids=question_ids,
        total_score=req.total_score,
        duration_minutes=req.duration_minutes,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # 返回详情（含完整题目）
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    # 按 question_ids 顺序排列
    q_map = {q.id: q for q in questions}
    ordered = [q_map[qid] for qid in question_ids if qid in q_map]

    return ExamDetailResponse(
        id=exam.id,
        title=exam.title,
        description=exam.description,
        question_ids=exam.question_ids,
        total_score=exam.total_score,
        duration_minutes=exam.duration_minutes,
        created_at=exam.created_at,
        questions=[QuestionResponse.model_validate(q) for q in ordered],
    )


@router.get("", response_model=ExamListResponse)
def list_exams(db: Session = Depends(get_db)):
    """试卷列表。"""
    exams = db.query(Exam).order_by(Exam.created_at.desc()).all()
    return ExamListResponse(items=exams, total=len(exams))


@router.get("/{exam_id}", response_model=ExamDetailResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    """试卷详情（含完整题目列表）。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")

    questions = db.query(Question).filter(Question.id.in_(exam.question_ids)).all()
    q_map = {q.id: q for q in questions}
    ordered = [q_map[qid] for qid in exam.question_ids if qid in q_map]

    return ExamDetailResponse(
        id=exam.id,
        title=exam.title,
        description=exam.description,
        question_ids=exam.question_ids,
        total_score=exam.total_score,
        duration_minutes=exam.duration_minutes,
        created_at=exam.created_at,
        questions=[QuestionResponse.model_validate(q) for q in ordered],
    )


@router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    """删除试卷。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    db.delete(exam)
    db.commit()
