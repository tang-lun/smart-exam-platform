import json
import re

from openai import APIStatusError, APIConnectionError, OpenAI

from app.config import settings

client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url, timeout=180.0, max_retries=2)

SYSTEM_PROMPT = """你是一位经验丰富的初中数学教师和出题专家。你的任务是根据指定的知识点、题型和难度，生成高质量的数学题目。

## 核心要求
1. 题目必须紧扣指定的知识点
2. 难度匹配用户要求（easy=基础概念, medium=常规应用, hard=综合拓展）
3. 题干表述清晰准确，符合初中生阅读水平
4. 选择题必须提供4个选项（A/B/C/D），其中只有一个正确答案，且答案必须能在4个选项中明确找到对应
5. 填空题答案需简洁明确
6. 计算题和证明题需给出完整解答过程（放在 answer_analysis 中）
7. 证明题的 answer 字段必须写最终结论（如"全等""成立"），answer_analysis 中写完整推导过程。answer 字段绝对不能写"略""见解析""证明略"等占位词，必须写出具体的数学结论

## 解析字数规定（极其重要，违反将导致生成失败）
- 基础题（easy）：解析 40-80 字，言简意赅，直击要点
- 中等题（medium）：解析 60-120 字，步骤清晰
- 较难题（hard）：解析 100-180 字，关键推导不省略
- 所有解析必须以"解："开头，直接写解题步骤，不铺垫不总结不评价
- 解析严禁超过 200 字，超过的部分会被截断
- 示例（标准长度）："解：由题意得 $2x+3=7$，移项得 $2x=4$，系数化为1得 $x=2$。"（约25字，基础题）

## 绝对禁止（核心铁律）
你生成的题目就是你出的，你的身份是"出题老师+解题老师"，不是"审题老师"。因此：
- 严禁在解析、题干、答案中出现"题目有误""计算有误""原题错误""更正""应改为""建议修改""此题不严谨""题干有歧义""答案有误""选项设置有误"等任何自我否定或纠错措辞
- 严禁评价题目质量，如"此题考查了""本题难度适中""题目设计巧妙"等
- 解析只做一件事：教学生如何从题干条件推导出答案。不审题、不评题、不改题
- 严禁在解析中写"根据原题""原题中""题目给出的"等暗示题目来自别处的措辞——你就是题目的唯一作者

## 题干规范
- 题干需简洁明了、题意完整，单道题题干不超过200字
- 题目必须纯文字描述，严禁依赖图片、图形、图表
- 严禁出现"如图""如图所示""如下图""见下图"等需要配合图片才能理解的表述
- 几何题必须用文字描述图形（如"在△ABC中，AB=AC，D是BC中点"），不得引用图片

## 填空题规范
- 留空横线直接用普通文本"______"（6个下划线）
- 严禁在 LaTeX 公式内使用 \\text{______}、\\underline{} 等命令表示填空
- 留空横线必须放在 $...$ 或 $$...$$ 定界符的外面

## 公式格式要求（极其重要）
- 所有数学表达式、公式、方程、符号必须使用 LaTeX 格式
- 行内公式使用 $...$ 包裹，如：$x^2 + 2x - 3 = 0$
- 独立公式使用 $$...$$ 包裹，如：$$y = ax^2 + bx + c$$
- 分数用 \\frac{}{}，根号用 \\sqrt{}，角用 \\angle，三角形用 \\triangle，度数用 ^\\circ
- 严禁使用英文变量名组合（如 "solve x"、"find y"、"sum of"），必须用中文表达
- 严禁出现英文单词或英文缩写，如 "cm" 改为"厘米"，"kg"改为"千克"
- 题干中的数字和单位必须用中文表达，如"5厘米"而不是"5cm"
- 选项中的数学公式也必须用 LaTeX 格式

## 题目正确性要求
- 答案必须正确无误，计算过程经得起检验
- 选择题的干扰项要有迷惑性但明显错误，不能出现两个正确选项
- 题干给出的条件必须充分，能够唯一确定答案
- 不要生成条件不足或条件矛盾的题目

示例（正确）：
"已知 $x^2 - 5x + 6 = 0$，求 $x$ 的值。"
"计算 $\\sqrt{27} + \\sqrt{12}$ 的值。"
"在 $\\triangle ABC$ 中，$\\angle A = 30^\\circ$，$AB = 5$ 厘米。"

示例（错误，绝对禁止）：
"solve the equation 2x + 3 = 7"
"find the value of y when x = 2"

你必须严格按照以下 JSON 数组格式输出，不要输出任何其他内容：

```json
[
  {
    "type": "choice",
    "stem": "题干内容（公式用LaTeX）",
    "options": ["A. 选项A（公式用LaTeX）", "B. 选项B", "C. 选项C", "D. 选项D"],
    "answer": "B",
    "answer_analysis": "解：解题步骤（简洁，不超过字数上限）",
    "knowledge_points": ["知识点1", "知识点2"],
    "difficulty": "medium"
  }
]
```

注意：
- type 取值：choice / fill_blank / calculation / proof
- difficulty 取值：easy / medium / hard
- 选择题的 answer 填正确选项字母（如 "B"），options 必须是一个包含4个字符串的数组，格式为 "A. xxx"
- 填空题 answer 填最终答案
- 计算题和证明题 answer 填最终结果，answer_analysis 填完整解答过程
- 所有公式必须 LaTeX 格式，所有文字必须中文
"""


def _fix_json_escapes(json_str: str) -> str:
    """修复 AI 返回的 JSON 中 LaTeX 反斜杠导致的非法转义序列。

    AI 可能在 JSON 字符串值里输出 \\sqrt、\\frac 等，
    Python json 解析器会把 \\s、\\f 等当成转义序列报错。
    """
    result = []
    in_string = False
    escape_next = False
    i = 0
    while i < len(json_str):
        ch = json_str[i]
        if escape_next:
            result.append(ch)
            escape_next = False
            i += 1
            continue
        if ch == '\\' and in_string:
            # 在 JSON 字符串内，\uXXXX 是合法 Unicode 转义，不能动
            rest = json_str[i+1:i+7]
            if i + 5 < len(json_str) and rest[0] == 'u' and all(c in '0123456789abcdefABCDEF' for c in rest[1:5]):
                result.append(ch)
                i += 1
                continue
            # 所有 \字母 都需要双写转义——AI 输出的是 LaTeX（\triangle \neq \frac 等），
            # 不是 JSON 转义序列。唯一例外是 \uXXXX（已在上面处理）。
            if i + 1 < len(json_str) and json_str[i + 1].isalpha():
                ch_next = json_str[i + 1]
                result.append('\\\\')
                result.append(ch_next)
                i += 2
                continue
            result.append(ch)
            escape_next = True
            i += 1
            continue
        if ch == '"':
            in_string = not in_string
        result.append(ch)
        i += 1
    return ''.join(result)


# 禁止在解析/题干/答案中出现的自我否定措辞（AI 有时会"纠正"自己生成的题目）
_SELF_CRITICISM_PATTERNS = [
    re.compile(r"题目有误[：:；;，,。\.]?"),
    re.compile(r"计算有误[：:；;，,。\.]?"),
    re.compile(r"原题[有错]误[：:；;，,。\.]?"),
    re.compile(r"更正题[目干][：:；;，,。\.]?"),
    re.compile(r"应改为[：:；;，,。\.]?"),
    re.compile(r"原题为[：:；;，,。\.]?"),
    re.compile(r"建议修改[为成]?"),
    re.compile(r"此题不严谨[，,。\.]?"),
    re.compile(r"题干有歧义[，,。\.]?"),
    re.compile(r"答案有误[：:；;，,。\.]?"),
    re.compile(r"选项设置有误[：:；;，,。\.]?"),
    re.compile(r"根据原题[：:；;，,。\.]?"),
    re.compile(r"题目中给出[的的]"),
    # 评价题目的措辞（解析不应该评价题目）
    re.compile(r"此题考查了[^，,。.]*[，,。.]?"),
    re.compile(r"本题难度[^，,。.]*[，,。.]?"),
    re.compile(r"题目设计[^，,。.]*[，,。.]?"),
]

# 解析字数上限（按难度）
_ANALYSIS_MAX_LEN = {"easy": 100, "medium": 150, "hard": 220}


def _strip_self_criticism(text: str) -> str:
    """移除 AI 输出中自我否定/纠错/评价题目的措辞。"""
    for pat in _SELF_CRITICISM_PATTERNS:
        text = pat.sub("", text)
    return text.strip()


def _trim_analysis(text: str, difficulty: str) -> str:
    """截断过长解析，保留完整句子。"""
    if not text:
        return text
    max_len = _ANALYSIS_MAX_LEN.get(difficulty, 150)
    if len(text) <= max_len:
        return text
    # 在 max_len 附近找句号/分号截断
    cut = max_len
    for sep in "。。；;，,":
        pos = text.rfind(sep, max_len - 30, max_len + 20)
        if pos > 0:
            cut = pos + 1
            break
    return text[:cut].rstrip()


def _post_validate_question(q: dict) -> list[str]:
    """对 AI 生成的题目做程序化校验，返回问题列表（空列表=通过）。"""
    issues = []
    stem = (q.get("stem") or "").strip()
    answer = (q.get("answer") or "").strip()
    analysis = (q.get("answer_analysis") or "").strip()
    qtype = q.get("type", "")
    options = q.get("options") or []
    diff = q.get("difficulty", "medium")

    if len(stem) < 5:
        issues.append("题干过短")
    if len(stem) > 300:
        issues.append(f"题干过长（{len(stem)}字）")

    # 选择题：答案必须是 A/B/C/D 之一
    if qtype == "choice":
        if answer.upper() not in ("A", "B", "C", "D"):
            issues.append(f"选择题答案'{answer}'不是A-D")
        if len(options) < 2:
            issues.append("选择题选项不足")
        # 检查答案确实在选项中
        opt_labels = [opt[:2].rstrip(". ").upper() for opt in options if opt]
        if answer.upper() in ("A", "B", "C", "D") and answer.upper() not in opt_labels:
            issues.append(f"答案{answer}不在选项标识中")

    # 解析过长
    max_analysis = _ANALYSIS_MAX_LEN.get(diff, 150)
    if len(analysis) > max_analysis + 50:
        issues.append(f"解析过长（{len(analysis)}字，上限{max_analysis}）")

    # 自否定检测
    for pat in _SELF_CRITICISM_PATTERNS:
        for field_name, field_val in [("题干", stem), ("答案", answer), ("解析", analysis)]:
            if pat.search(field_val):
                issues.append(f"{field_name}含自否定句式")
                break

    # 禁止依赖图片的表述
    if re.search(r"如图|如图所示|如下图|见下图|见右图", stem):
        issues.append("题干含图片依赖表述")

    return issues


def _extract_json(text: str) -> str:
    """从 API 返回的文本中提取 JSON 部分。"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", text)
    if match:
        return match.group(0)
    return text


def generate_questions(
    knowledge_points: list[str],
    question_type: str = "choice",
    count: int = 5,
    difficulty: str = "medium",
    grade_level: str = "grade_7",
) -> list[dict]:
    """调用 DeepSeek API 生成题目，返回题目 dict 列表。"""
    type_names = {
        "choice": "选择题",
        "fill_blank": "填空题",
        "calculation": "计算题",
        "proof": "证明题",
    }
    grade_names = {"grade_7": "初一", "grade_8": "初二", "grade_9": "初三"}
    diff_names = {"easy": "基础", "medium": "中等", "hard": "较难"}

    # 证明题和计算题逐题生成，避免一次输出过长导致超时/截断
    batch_size = count
    if question_type in ("proof", "calculation"):
        batch_size = 1

    all_data = []
    for start in range(0, count, batch_size):
        n = min(batch_size, count - start)

        user_message = (
            f"请生成 {n} 道{grade_names.get(grade_level, grade_level)}数学"
            f"{type_names.get(question_type, question_type)}，"
            f"知识点：{'、'.join(knowledge_points)}，"
            f"难度：{diff_names.get(difficulty, difficulty)}。"
            f"请严格按照 JSON 数组格式输出。"
        )

        try:
            response = client.chat.completions.create(
                model=settings.ai_model,
                max_tokens=8192,
                temperature=0.8,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            )
        except APIConnectionError:
            raise ValueError("连接 AI 服务失败，请检查网络后重试")
        except APIStatusError as e:
            if e.status_code >= 500:
                raise ValueError("AI 服务暂时繁忙，请稍后重试")
            raise ValueError(f"AI 服务返回错误 (HTTP {e.status_code})，请检查 API Key 是否有效")

        raw_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "length":
            raise ValueError("AI 输出被截断（达到 token 上限），请减少题目数量或降低难度后重试")

        json_str = _extract_json(raw_text)
        # 先修复 LaTeX 反斜杠（必须放在 json.loads 之前，因为 \t \f \n 等是合法 JSON 转义，
        # json.loads 不会报错而是直接转成 Tab/换页/换行符，导致 \triangle \frac \sqrt 损坏）
        json_str = _fix_json_escapes(json_str)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            fixed = json_str.replace("'", '"')
            try:
                data = json.loads(fixed)
            except json.JSONDecodeError as e:
                raise ValueError(f"AI 返回的 JSON 格式无法解析。请重试。原始错误: {e.msg}") from e

        all_data.extend(data)

    # 后处理：清洗自否定文字、截断过长解析、程序化校验
    for q in all_data:
        q["stem"] = _strip_self_criticism(q.get("stem", "")).strip()
        q["answer"] = _strip_self_criticism(q.get("answer", "")).strip()
        raw_analysis = q.get("answer_analysis", "") or ""
        raw_analysis = _strip_self_criticism(raw_analysis)
        q["answer_analysis"] = _trim_analysis(raw_analysis, q.get("difficulty", difficulty))
        # 校验（仅记录日志，不阻断——提示词已经约束，程序校验作为安全网）
        issues = _post_validate_question(q)
        if issues:
            q.setdefault("_warnings", issues)

    return all_data


def analyze_exam(exam_data: dict) -> dict:
    """AI 分析试卷质量，返回评分和适合的学生群体。"""
    questions = exam_data.get("questions", [])
    if not questions:
        return {"score": 0, "summary": "试卷为空", "suitable_for": "", "strengths": [], "weaknesses": []}

    qlist = []
    for q in questions:
        qlist.append({
            "type": q.get("type", ""),
            "diff": q.get("difficulty", ""),
            "kps": q.get("knowledge_points", []),
            "stem": (q.get("stem", "") or "")[:60],
        })

    # 统计难度分布
    from collections import Counter
    diff_count = Counter(q.get("difficulty", "") for q in questions)
    type_count = Counter(q.get("type", "") for q in questions)

    prompt = f"""请分析下面这份初中数学试卷的整体难度和适合的学生群体。

试卷信息：
- 总题数：{exam_data.get('total_questions', len(questions))}
- 总分：{exam_data.get('total_score', 100)}分
- 时长：{exam_data.get('duration_minutes', 60)}分钟
- 难度分布：{dict(diff_count)}
- 题型分布：{dict(type_count)}
- 题目列表：{qlist}

请按以下格式回复 JSON（各项数值请根据实际分析给出，不要照抄示例数字）：
```json
{{"difficulty_score": 0, "difficulty_label": "", "overall_score": 0, "summary": "", "suitable_for": "", "strengths": [], "weaknesses": []}}
```

其中 difficulty_score 为 0-100（0=极简单 50=中等 100=极难），difficulty_label 为难度描述，overall_score 为 0-100 综合评分（从题型搭配25分+难度梯度25分+知识点覆盖25分+题目质量25分四个维度加总）。"""

    try:
        response = client.chat.completions.create(
            model=settings.ai_model,
            max_tokens=512,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content
        json_str = _extract_json(raw)
        return json.loads(json_str)
    except Exception:
        return {
            "score": 0,
            "summary": "分析暂时不可用",
            "suitable_for": "",
            "strengths": [],
            "weaknesses": [],
        }


def generate_analysis(q: dict) -> str:
    """用 AI 为题目生成解析（答案分析）。"""
    diff = q.get("difficulty", "medium")
    diff_label = {"easy": "基础", "medium": "中等", "hard": "较难"}.get(diff, diff)
    max_words = {"easy": 80, "medium": 120, "hard": 180}.get(diff, 120)

    prompt = f"""你是初中数学老师，请为下面这道题写出解答过程。

题目信息：
- 题型：{q.get('type')}
- 题干：{q.get('stem')}
- 答案：{q.get('answer')}
- 难度：{diff_label}

要求：
1. 以"解："开头直接写解题步骤，{max_words}字以内
2. 不铺垫、不总结、不评价题目难度或质量
3. 严禁说"题目有误""计算错误""根据原题"等任何审题/纠错措辞，你是解题者
4. 直接输出解析文字，不需要JSON格式"""

    try:
        response = client.chat.completions.create(
            model=settings.ai_model,
            max_tokens=200,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()
        raw = _strip_self_criticism(raw)
        return _trim_analysis(raw, diff)
    except Exception:
        return ""


def _precheck_difficulty(q: dict) -> str | None:
    """程序化预检：检查明显不合理的题目。返回 None 表示通过，返回字符串为问题描述。"""
    stem = (q.get("stem") or "").strip()
    answer = (q.get("answer") or "").strip()
    analysis = (q.get("answer_analysis") or "").strip()
    diff = q.get("difficulty", "")
    qtype = q.get("type", "")

    # 题干过短 + hard
    if len(stem) <= 5 and diff == "hard":
        return f"题干过短（{len(stem)}字），不可能达到较难水平"

    # 题干含图片依赖
    if re.search(r"如图|如图所示|如下图|见下图|见右图", stem):
        return "题干含图片依赖表述，请用纯文字描述"

    # 选择题答案必须是 A-D
    if qtype == "choice" and answer.upper() not in ("A", "B", "C", "D"):
        return f"选择题答案必须是A-D之一，当前为'{answer}'"

    # 解析含自否定句式（直接拒绝）
    for field_name, field_val in [("题干", stem), ("答案", answer), ("解析", analysis)]:
        for pat in _SELF_CRITICISM_PATTERNS:
            if pat.search(field_val):
                return f"{field_name}含不当措辞（如'题目有误'等），请修改后重试"

    return None


def validate_question(q: dict) -> dict:
    """使用 AI 审核手动创建的题目是否合理、有解。返回 {"valid": bool, "feedback": str}。"""

    # 程序化预检
    precheck = _precheck_difficulty(q)
    if precheck:
        return {"valid": False, "feedback": precheck}

    # 先清洗自否定文字再送审
    stem = _strip_self_criticism(q.get("stem", "")).strip()
    answer = _strip_self_criticism(q.get("answer", "")).strip()
    analysis = _strip_self_criticism((q.get("answer_analysis") or "").strip())
    diff_name = {"easy": "基础", "medium": "中等", "hard": "较难"}.get(q.get("difficulty"), q.get("difficulty"))

    prompt = f"""你是初中数学题目审核员，请温和地审核下面这道题。

## 审核原则
- 主要检查：答案是否正确、题目能否求解、有无知识性错误
- 难度标注仅作参考建议，除非明显离谱（如"解1+1"标为较难），否则不要因难度问题判不通过
- 计算题即使题干简短，只要答案正确、可求解，就应通过
- 不要因为你没见过的表述方式而判错，只关注实质性的数学错误

## 审核项目（按优先级）
1. 答案是否正确（最重要——请实际演算验证）
2. 题目是否可求解、条件是否充分
3. 是否有知识性错误
4. 难度标注是否明显不合理

题目：{stem}
题型：{q.get('type')}
知识点：{', '.join(q.get('knowledge_points', []))}
难度标注：{q.get('difficulty')}（{diff_name}）
答案：{answer}
解析：{analysis or '无'}

请只输出 JSON：
```json
{{"valid": true或false, "feedback": "通过写'题目合格'或附带温和建议；不通过写具体原因"}}
```"""

    try:
        response = client.chat.completions.create(
            model=settings.ai_model,
            max_tokens=512,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
    except APIConnectionError:
        return {"valid": True, "feedback": "AI 审核暂时不可用，允许保存"}
    except APIStatusError:
        return {"valid": True, "feedback": "AI 审核暂时不可用，允许保存"}

    raw_text = response.choices[0].message.content
    json_str = _extract_json(raw_text)

    try:
        result = json.loads(json_str)
        return {"valid": result.get("valid", True), "feedback": result.get("feedback", "")}
    except json.JSONDecodeError:
        return {"valid": True, "feedback": "AI 审核结果解析失败，允许保存（请人工核对）"}
