<div align="center">

# 智能题库与试卷生成平台

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vuedotjs)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

面向初中数学的 **AI 出题 × 智能组卷** 平台。AI 生成题目、AI 审核把关、AI 自动组卷、在线答题评分、Word 试卷导出 —— 覆盖从出题到考试的完整流程。

</div>

---

## 核心能力

<table>
<tr>
<td width="50%">

**📝 AI 批量出题**  
指定知识点、题型、数量、难度，大模型批量生成。自动去重，生成的题目直接入库。

**🛡️ AI 审核把关**  
手动出题后 AI 自动审核题目质量与答案正确性，不通过会给出修改建议。

**📂 批量导入**  
CSV / Excel 模板导入，中英文表头自动识别，懒人友好。

</td>
<td width="50%">

**🧠 AI 自动组卷**  
设置题型分布、难度比例、总分，AI 自动从题库抽题组卷并分配分值。

**📄 导出 Word 试卷**  
一键导出 .docx，LaTeX 公式自动转 Word EQ 域，带参考答案与解析。

**✍️ 在线答题 × 自动判分**  
学生在平台答卷，选择/填空/计算/证明题自动评分，留存答题历史。

</td>
</tr>
</table>

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | Vue 3 · Vite · Element Plus · Pinia |
| 数学渲染 | KaTeX |
| 后端框架 | FastAPI · SQLAlchemy · Pydantic |
| 认证 | JWT (python-jose) + bcrypt |
| AI 接口 | OpenAI 兼容 API（GPT-4o / DeepSeek 等任意兼容模型） |
| 文档导出 | python-docx · openpyxl |
| 数据库 | SQLite（可替换为 PostgreSQL） |

## 快速启动

### 环境要求

- Python 3.10+
- Node.js 18+
- OpenAI 兼容 API Key

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate     # macOS / Linux
venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

创建 `.env`:

```env
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
JWT_SECRET=your-secret-key
```

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Swagger 文档 → http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 → http://localhost:5173

### 可选：填充示例数据

```bash
cd backend
python seed.py
```

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/          # 路由层：auth · questions · exams
│   │   ├── models/       # User · Question · Exam · ExamResult
│   │   ├── schemas/      # Pydantic 请求/响应模型
│   │   ├── services/     # AI 服务 · 组卷引擎 · 认证
│   │   ├── db/           # 数据库连接与会话
│   │   └── main.py       # 应用入口
│   ├── requirements.txt
│   ├── seed.py
│   └── app.db
├── frontend/
│   ├── src/
│   │   ├── api/          # Axios 封装
│   │   ├── components/   # 通用组件
│   │   ├── views/        # 页面组件
│   │   ├── stores/       # Pinia 状态
│   │   └── router/       # 路由配置
│   └── package.json
└── README.md
```

## API 一览

| 模块 | 端点 | 说明 |
|------|------|------|
| 🔐 Auth | `POST /api/auth/register` | 注册（教师/学生） |
| | `POST /api/auth/login` | 登录 |
| | `GET /api/auth/me` | 当前用户 |
| 📝 题目 | `POST /api/questions/generate` | AI 生成题目 |
| | `POST /api/questions/manual` | 手动创建（AI 审核） |
| | `POST /api/questions/import` | CSV/Excel 导入 |
| | `POST /api/questions/validate` | AI 审核（不保存） |
| | `GET /api/questions` | 列表 · 分页 · 筛选 · 搜索 |
| | `GET /api/questions/{id}` | 详情 |
| | `PUT /api/questions/{id}` | 编辑 |
| | `DELETE /api/questions/{id}` | 删除 |
| | `POST /api/questions/{id}/favorite` | 收藏/取消 |
| | `GET /api/questions/favorites/list` | 收藏列表 |
| | `GET /api/questions/template/download` | 下载导入模板 |
| 📋 试卷 | `POST /api/exams` | 创建试卷（手动/AI 组卷） |
| | `GET /api/exams` | 试卷列表 |
| | `GET /api/exams/{id}` | 试卷详情（含题目） |
| | `GET /api/exams/{id}/analyze` | AI 试卷分析 |
| | `GET /api/exams/{id}/export` | 导出 Word |
| | `POST /api/exams/{id}/submit` | 提交答卷 · 自动判分 |
| | `GET /api/exams/{id}/results` | 答题记录 |
| | `DELETE /api/exams/{id}` | 删除试卷 |
| 📊 系统 | `GET /api/stats` | 仪表盘统计 |
| | `GET /api/health` | 健康检查 |

---

<div align="center">

**💡 提示：** 搭配 DeepSeek 等国产模型使用，成本更低、国内访问更稳定。

</div>
