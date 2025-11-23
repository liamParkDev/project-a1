from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
import db.crud as crud
from core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_admin,
    decode_token,
)

router = APIRouter(prefix="/users", tags=["Users"])


# --------- Pydantic 스키마 ---------

class UserRegister(BaseModel):
    email: str
    password: str
    nickname: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserMe(BaseModel):
    id: int
    email: str
    nickname: str
    role: str

    class Config:
        orm_mode = True


# --------- API 엔드포인트 ---------

@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = crud.create_user(db, payload.email, payload.password, payload.nickname)
    return {"status": "ok", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(refresh_token: str):
    """
    Refresh Token으로 Access Token 재발급
    (Body나 Query로 refresh_token 받는 단순 버전)
    """
    payload = decode_token(refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = int(payload.get("sub"))
    # 여기서는 DB까지 안 가고 user_id만 가지고 새 토큰 발급 (필요하면 DB 조회 추가 가능)
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.get("/me", response_model=UserMe)
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/admin-only", response_model=UserMe)
def admin_only(current_admin=Depends(get_current_admin)):
    """
    관리자만 접근 가능한 API 예시
    """
    return current_admin
