import json
import re

from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)

SYSTEM_PROMPT = """你是一位经验丰富的初中数学教师和出题专家。你的任务是根据指定的知识点、题型和难度，生成高质量的数学题目。

要求：
1. 题目必须紧扣指定的知识点
2. 难度匹配用户要求（easy=基础概念, medium=常规应用, hard=综合拓展）
3. 题干表述清晰准确，符合初中生阅读水平
4. 选择题必须提供4个选项（A/B/C/D），其中只有一个正确答案
5. 填空题答案需简洁明确
6. 计算题和证明题需给出完整解答过程（放在 answer_analysis 中）
7. 每道题都要有简明的解析

你必须严格按照以下 JSON 数组格式输出，不要输出任何其他内容：

```json
[
  {
    "type": "choice",
    "stem": "题干内容",
    "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
    "answer": "B",
    "answer_analysis": "解析内容",
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
"""


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

    user_message = (
        f"请生成 {count} 道{grade_names.get(grade_level, grade_level)}数学"
        f"{type_names.get(question_type, question_type)}，"
        f"知识点：{'、'.join(knowledge_points)}，"
        f"难度：{diff_names.get(difficulty, difficulty)}。"
        f"请严格按照 JSON 数组格式输出。"
    )

    response = client.chat.completions.create(
        model=settings.ai_model,
        max_tokens=8192,
        temperature=0.8,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason
    if finish_reason == "length":
        raise ValueError("AI 输出被截断（达到 token 上限），请减少题目数量或降低难度后重试")

    json_str = _extract_json(raw_text)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # 尝试修复单引号、尾部逗号等常见 JSON 问题
        fixed = json_str.replace("'", '"')
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError:
            raise ValueError(f"AI 返回的 JSON 格式无法解析。请重试。原始错误: {e.msg}") from e

    return data
