"""种子数据生成：为初一数学生成覆盖 4题型×3难度 的均衡题库。"""
import sys
from app.db.database import SessionLocal, Base, engine
from app.models.question import Question, QuestionType, Difficulty, QuestionSource
from app.models.user import User, UserRole
from app.services.ai_service import generate_questions
from app.services.auth_service import hash_password

TYPES = ["choice", "fill_blank", "calculation", "proof"]
DIFFICULTIES = ["easy", "medium", "hard"]
GRADE = "grade_7"

# 每个题型+难度组合要生成的目标数量
TARGET_PER_COMBO = 5

TOPICS_POOL = [
    "一元一次方程", "二元一次方程组", "不等式", "整式的加减",
    "一元一次不等式", "一次函数", "相交线与平行线", "三角形",
    "实数", "平面直角坐标系", "数据的收集与整理", "统计与概率",
]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def _get_or_create_admin(db):
    admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if admin is None:
        admin = User(
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.admin,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"已创建管理员账户: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    return admin


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin = _get_or_create_admin(db)
    owner_id = admin.id

    done = 0
    total = len(TYPES) * len(DIFFICULTIES)

    for qtype in TYPES:
        for diff in DIFFICULTIES:
            # 检查已有数量（仅统计该用户的题目）
            existing = db.query(Question).filter(
                Question.type == qtype,
                Question.difficulty == diff,
                Question.owner_id == owner_id,
            ).count()

            need = TARGET_PER_COMBO - existing
            if need <= 0:
                done += 1
                print(f"[{qtype}/{diff}] 已有 {existing} 题，跳过")
                continue

            # 每批生成最多5题，不够再追
            while need > 0:
                batch = min(need, 5)
                # 随机选知识点
                import random
                kps = random.sample(TOPICS_POOL, min(3, len(TOPICS_POOL)))
                print(f"[{qtype}/{diff}] 需要 {need}，本批生成 {batch}，知识点：{kps}")

                try:
                    raw = generate_questions(
                        knowledge_points=kps,
                        question_type=qtype,
                        count=batch,
                        difficulty=diff,
                        grade_level=GRADE,
                    )
                except Exception as e:
                    print(f"  生成失败: {e}")
                    break

                for q in raw:
                    question = Question(
                        type=q.get("type", qtype),
                        subject="math",
                        grade_level=GRADE,
                        knowledge_points=q.get("knowledge_points", kps),
                        difficulty=q.get("difficulty", diff),
                        stem=q["stem"],
                        options=q.get("options"),
                        answer=q["answer"],
                        answer_analysis=q.get("answer_analysis"),
                        source=QuestionSource.ai_generated,
                        owner_id=owner_id,
                    )
                    db.add(question)
                    need -= 1

                db.commit()
                print(f"  已存入，剩余 {need}")

            done += 1
            print(f"进度: {done}/{total}")

    # 最终统计
    print("\n=== 题库分布 ===")
    from collections import Counter
    td = Counter()
    for q in db.query(Question).filter(Question.owner_id == owner_id).all():
        td[(q.type.value, q.difficulty.value)] += 1
    for (t, d), c in sorted(td.items()):
        print(f"  {t:15s} {d:8s} {c}")

    db.close()
    print("\n种子数据生成完毕。")


if __name__ == "__main__":
    main()
