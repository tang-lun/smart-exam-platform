from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import exams, questions
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="智能题库与试卷生成平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(exams.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
