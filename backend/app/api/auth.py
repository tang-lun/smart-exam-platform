from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserInfo
from app.services.auth_service import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """注册新用户。"""
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    if req.role not in ("teacher", "student"):
        raise HTTPException(status_code=400, detail="角色只能是 teacher 或 student")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=UserRole(req.role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "role": user.role.value},
    )


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录。"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "role": user.role.value},
    )


@router.get("/me", response_model=UserInfo)
def me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
    )
