import random

from sqlalchemy.orm import Session

from app.models.question import Question

# 中考数学题型分值参考（150分卷标准）
# 选择题 3-4分/题，填空题 3-4分/题，计算题 6-12分/题，证明题 8-14分/题
TYPE_SCORE_RANGES = {
    "choice": (3, 4),
    "fill_blank": (3, 4),
    "calculation": (6, 12),
    "proof": (8, 14),
}


def allocate_question_scores(
    questions: list[Question],
    exam_total_score: int,
    type_distribution: dict[str, int],
    difficulty_distribution: dict[str, int],
) -> dict[str, int]:
    """参考中考分值分布，为每道题分配分值。

    规则：
    1. 按题型分配基准分（选择/填空低分，计算/证明高分）
    2. 同题型内，较难题分值略高
    3. 微调使总分精确匹配 exam_total_score
    返回 {"0": 4, "1": 4, ...} 格式（key 为题号索引字符串）
    """
    if not questions:
        return {}

    total_questions = len(questions)
    if total_questions == 0:
        return {}

    # 第一步：按题型分组（从实际题目出发，保证每道题都有归属）
    type_lists: dict[str, list] = {}
    for q in questions:
        qtype = q.type.value if hasattr(q.type, 'value') else str(q.type)
        type_lists.setdefault(qtype, []).append(q)

    # 第二步：计算每种题型的总预算（以 type_distribution 为权重参考）
    type_budgets: dict[str, int] = {}
    for qtype, qlist in type_lists.items():
        lo, hi = TYPE_SCORE_RANGES.get(qtype, (3, 10))
        avg_per_q = (lo + hi) / 2
        type_budgets[qtype] = int(avg_per_q * len(qlist))

    # 按比例缩放使总分接近 exam_total_score
    budget_total = sum(type_budgets.values())
    if budget_total > 0:
        scale = exam_total_score / budget_total
        for qtype in type_budgets:
            type_budgets[qtype] = round(type_budgets[qtype] * scale)

    # 微调使总预算精确等于 exam_total_score
    diff = exam_total_score - sum(type_budgets.values())
    # 把差额加到计算题预算上（计算题数量通常最多，调节最自然）
    if diff != 0 and "calculation" in type_budgets:
        type_budgets["calculation"] += diff
    elif diff != 0 and type_budgets:
        first_type = list(type_budgets.keys())[0]
        type_budgets[first_type] += diff

    # 第二步：在每种题型内按难度分配具体分值
    scores = {}
    idx = 0
    q_idx_map = {}  # q_id -> index in questions list
    for i, q in enumerate(questions):
        q_idx_map[q.id] = i

    for qtype, qlist in type_lists.items():
        if not qlist:
            continue
        budget = type_budgets[qtype]
        lo, hi = TYPE_SCORE_RANGES.get(qtype, (3, 10))

        # 按难度排序：easy → medium → hard
        diff_order = {"easy": 0, "medium": 1, "hard": 2}
        qlist.sort(key=lambda q: diff_order.get(
            q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty), 1
        ))

        # 为每道题分配初始分（难度越高分越高）
        raw_scores = []
        for q in qlist:
            diff = q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty)
            if diff == "hard":
                raw_scores.append(hi)
            elif diff == "medium":
                raw_scores.append((lo + hi) // 2)
            else:
                raw_scores.append(lo)

        # 缩放到预算
        raw_total = sum(raw_scores)
        if raw_total > 0:
            scale = budget / raw_total
            final_q_scores = [max(1, round(s * scale)) for s in raw_scores]
        else:
            final_q_scores = [budget // len(qlist)] * len(qlist)

        # 微调到精确预算
        final_diff = budget - sum(final_q_scores)
        # 在较难的题上加减
        if final_diff != 0:
            step = 1 if final_diff > 0 else -1
            for j in range(len(final_q_scores) - 1, -1, -1):
                if final_diff == 0:
                    break
                lo_j, hi_j = TYPE_SCORE_RANGES.get(qtype, (1, 15))
                new_val = final_q_scores[j] + step
                if lo_j <= new_val <= hi_j:
                    final_q_scores[j] = new_val
                    final_diff -= step

        for q, s in zip(qlist, final_q_scores):
            idx_in_list = q_idx_map[q.id]
            scores[str(idx_in_list)] = s

    return scores


def _pick_candidates(db: Session, qtype: str, diff: str, n: int, knowledge_points: list[str], grade_levels: list[str] | None = None, owner_id: int | None = None) -> list[Question]:
    """从题库中按题型、难度、知识点、学段选取 n 道题，不够则返回实际数量。"""
    query = db.query(Question).filter(Question.type == qtype, Question.difficulty == diff)

    if owner_id is not None:
        query = query.filter(Question.owner_id == owner_id)

    if grade_levels:
        query = query.filter(Question.grade_level.in_(grade_levels))

    if knowledge_points:
        # SQL 级别过滤：JSON 数组中 LIKE 匹配知识点
        from sqlalchemy import or_
        kp_filters = [Question.knowledge_points.like(f'%"{kp}"%') for kp in knowledge_points]
        query = query.filter(or_(*kp_filters))

    candidates = query.all()

    if len(candidates) <= n:
        return candidates
    return random.sample(candidates, n)


def auto_select_questions(
    db: Session,
    knowledge_points: list[str],
    difficulty_distribution: dict[str, int],
    type_distribution: dict[str, int],
    grade_levels: list[str] | None = None,
    owner_id: int | None = None,
) -> list[Question]:
    """按题型和难度分布从题库中自动选题，不够时跨难度补充。"""
    selected = []
    all_diffs = list(difficulty_distribution.keys())

    for qtype, type_count in type_distribution.items():
        if type_count <= 0:
            continue

        # 计算该题型在各难度下的期望数量（按百分比分配）
        diff_needed = {}
        for diff, pct in difficulty_distribution.items():
            diff_needed[diff] = round(type_count * pct / 100)
        # 修正舍入误差
        diff_total = sum(diff_needed.values())
        if diff_total != type_count:
            max_diff = max(difficulty_distribution, key=difficulty_distribution.get)
            diff_needed[max_diff] += type_count - diff_total
        # 保证每种题型至少有一道中等或难题（除非该题型总数≤1）
        if type_count > 1 and diff_needed.get("medium", 0) + diff_needed.get("hard", 0) == 0:
            diff_needed["easy"] -= 1
            diff_needed["medium"] = (diff_needed.get("medium", 0) or 0) + 1

        # 先按难度匹配
        picked_ids = set()
        for diff, n in diff_needed.items():
            if n <= 0:
                continue
            candidates = _pick_candidates(db, qtype, diff, n, knowledge_points, grade_levels, owner_id=owner_id)
            for q in candidates:
                if q.id not in picked_ids:
                    selected.append(q)
                    picked_ids.add(q.id)

        # 不够的从同题型其他难度补（放宽知识点限制）
        shortage = type_count - len(picked_ids)
        if shortage > 0:
            for diff in all_diffs:
                if shortage <= 0:
                    break
                candidates = _pick_candidates(db, qtype, diff, shortage + 5, knowledge_points if len(picked_ids) == 0 else [], grade_levels, owner_id=owner_id)
                for q in candidates:
                    if q.id not in picked_ids and shortage > 0:
                        selected.append(q)
                        picked_ids.add(q.id)
                        shortage -= 1

        # 仍不够则无视学段限制补足
        shortage = type_count - len(picked_ids)
        if shortage > 0:
            for diff in all_diffs:
                if shortage <= 0:
                    break
                candidates = _pick_candidates(db, qtype, diff, shortage + 5, [], [], owner_id=owner_id)
                for q in candidates:
                    if q.id not in picked_ids and shortage > 0:
                        selected.append(q)
                        picked_ids.add(q.id)
                        shortage -= 1

    # 严格按题型顺序：选择→填空→计算→证明，同题型内易→难
    type_order = {"choice": 0, "fill_blank": 1, "calculation": 2, "proof": 3}
    diff_order = {"easy": 0, "medium": 1, "hard": 2}
    selected.sort(key=lambda q: (
        type_order.get(q.type.value if hasattr(q.type, 'value') else str(q.type), 99),
        diff_order.get(q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty), 99),
    ))
    return selected
