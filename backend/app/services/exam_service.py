import random

from sqlalchemy.orm import Session

from app.models.question import Question


def auto_select_questions(
    db: Session,
    knowledge_points: list[str],
    question_count: int,
    difficulty_distribution: dict[str, int],
) -> list[Question]:
    """根据条件从题库中自动选题，按难度分布随机抽取。"""
    selected = []
    for difficulty, percentage in difficulty_distribution.items():
        n = round(question_count * percentage / 100)
        if n == 0:
            continue

        query = db.query(Question).filter(Question.difficulty == difficulty)
        if knowledge_points:
            # 筛选包含任一指定知识点的题目（JSON 数组包含匹配）
            candidates = query.all()
            candidates = [
                q for q in candidates
                if any(kp in q.knowledge_points for kp in knowledge_points)
            ]
        else:
            candidates = query.all()

        if len(candidates) <= n:
            selected.extend(candidates)
        else:
            selected.extend(random.sample(candidates, n))

    return selected
