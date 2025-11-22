from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
import db.crud as crud
from core.security import create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


# --------- Pydantic 스키마 ---------

class UserRegister(BaseModel):
    email: str
    password: str
    nickname: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserMe(BaseModel):
    id: int
    email: str
    nickname: str

    class Config:
        orm_mode = True


# --------- API 엔드포인트 ---------

@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = crud.create_user(db, payload.email, payload.password, payload.nickname)
    return {"status": "ok", "user_id": user.id}


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        # 기존처럼 status: error 리턴해도 되는데, HTTP 401 쓰는 게 더 정석
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # JWT 토큰 생성 (sub에 user_id 넣기)
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "status": "ok",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
    }


@router.get("/me", response_model=UserMe)
def read_me(current_user = Depends(get_current_user)):
    # get_current_user 가 models.User 객체를 리턴하니까 그대로 넘겨도 됨
    return current_user
