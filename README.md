# 智能题库与试卷生成平台

面向初中数学的 AI 出题与组卷 MVP 平台。支持 AI 批量生成题目、手动出题 AI 审核、CSV/Excel 批量导入题库，以及手动选题或 AI 自动组卷，提供在线答题、自动评分与 Word 试卷导出。

## 功能概览

### 题库管理
- **AI 批量出题** — 指定知识点、题型、数量、难度、学段，调用大模型自动生成题目
- **手动出题 × AI 审核** — 手动录入题目，AI 审核题目质量与答案正确性
- **批量导入** — 支持 CSV / Excel (.xlsx) 模板导入，自动去重
- **题库检索** — 按题型、难度、学段、知识点、关键词筛选与分页浏览
- **收藏与编辑** — 收藏题目、编辑题目信息、删除题目

### 试卷管理
- **手动选题组卷** — 从题库中挑选题目，自动分配分值
- **AI 自动组卷** — 指定知识点、题型分布、难度分布、总分，AI 自动从题库中组卷
- **试卷分析** — AI 分析试卷难度结构、知识点覆盖、给出评价与适用学生群体建议
- **导出 Word** — 将试卷（含参考答案与解析）导出为 .docx，支持数学公式
- **在线答题** — 学生在平台内答卷，自动判分并保存答题记录

### 其他
- 教师/学生双角色注册登录（JWT 鉴权）
- 仪表盘概览（题目总量、AI 出题数、试卷数、今日新增）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3, Vite, Element Plus, Vue Router, Pinia, Axios, KaTeX |
| 后端 | FastAPI, SQLAlchemy, Pydantic, python-jose (JWT), bcrypt |
| AI | OpenAI 兼容 API（可接入任意兼容模型） |
| 导出 | python-docx（Word 文档）、openpyxl（Excel 导入） |
| 数据库 | SQLite（开发） |

## 快速启动

### 1. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

创建 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
JWT_SECRET=your-secret-key
```

启动服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档：http://localhost:8000/docs

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器：http://localhost:5173

### 3. 数据库初始化

```bash
cd backend
python seed.py    # 可选：填充示例数据
```

数据库文件会自动创建于 `backend/app.db`。

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── api/             # 路由：auth, questions, exams
│   │   ├── models/          # 数据模型：User, Question, Exam, ExamResult
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── services/        # 业务逻辑：AI 服务、组卷服务、认证服务
│   │   ├── db/              # 数据库连接与会话管理
│   │   └── main.py          # FastAPI 入口
│   ├── requirements.txt
│   ├── seed.py              # 示例数据脚本
│   └── app.db               # SQLite 数据库文件
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios 封装与 API 接口
│   │   ├── components/      # 通用组件
│   │   ├── views/           # 页面组件
│   │   ├── stores/          # Pinia 状态管理
│   │   └── router/          # Vue Router 路由配置
│   ├── vite.config.js       # Vite 配置（含 /api 代理）
│   └── package.json
└── README.md
```

## API 概览

| 模块 | 端点 | 说明 |
|------|------|------|
| Auth | `POST /api/auth/register` | 注册 |
| Auth | `POST /api/auth/login` | 登录 |
| Auth | `GET /api/auth/me` | 当前用户信息 |
| 题目 | `POST /api/questions/generate` | AI 生成题目 |
| 题目 | `POST /api/questions/manual` | 手动创建（AI 审核） |
| 题目 | `POST /api/questions/import` | CSV/Excel 批量导入 |
| 题目 | `GET /api/questions` | 题目列表（分页/筛选） |
| 题目 | `GET /api/questions/{id}` | 题目详情 |
| 题目 | `PUT /api/questions/{id}` | 编辑题目 |
| 题目 | `POST /api/questions/{id}/favorite` | 收藏/取消 |
| 题目 | `DELETE /api/questions/{id}` | 删除题目 |
| 题目 | `POST /api/questions/validate` | AI 审核（不保存） |
| 题目 | `GET /api/questions/template/download` | 下载导入模板 |
| 试卷 | `POST /api/exams` | 创建试卷 |
| 试卷 | `GET /api/exams` | 试卷列表 |
| 试卷 | `GET /api/exams/{id}` | 试卷详情 |
| 试卷 | `GET /api/exams/{id}/analyze` | AI 试卷分析 |
| 试卷 | `GET /api/exams/{id}/export` | 导出 Word |
| 试卷 | `POST /api/exams/{id}/submit` | 提交答卷 |
| 试卷 | `GET /api/exams/{id}/results` | 答题记录 |
| 系统 | `GET /api/stats` | 仪表盘统计 |
| 系统 | `GET /api/health` | 健康检查 |
