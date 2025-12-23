# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.security import verify_password, get_password_hash, set_auth_cookies
from db.models import User, UserRole
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
        from_attributes = True

class UserMeResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    profile_image: str | None
    role: UserRole

    class Config:
        from_attributes = True

@router.post("/register")
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    user = crud.create_user(
        db,
        payload.email,
        payload.password,
        payload.nickname,
        profile_complete=True,
    )
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    db.commit()
    set_auth_cookies(response, access_token, refresh_token)
    return {"status": "ok", "user_id": user.id, "access_token": access_token, "refresh_token": refresh_token}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    db.commit()
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/admin-only", response_model=UserMe)
def admin_only(current_admin=Depends(get_current_admin)):
    return current_admin

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change-password")
def change_password(
    req: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.password_hash or not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="기존 패스워드가 일치하지 않습니다.")

    current_user.password_hash = get_password_hash(req.new_password)
    db.commit()

    return {"message": "비밀번호가 변경되었습니다."}

class ProfileUpdateRequest(BaseModel):
    nickname: str | None = None
    profile_image: str | None = None

@router.post("/update-profile")
def update_profile(
    req: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if req.nickname:
        current_user.nickname = req.nickname
    if req.profile_image:
        current_user.profile_image = req.profile_image

    db.commit()
    db.refresh(current_user)

    return {"message": "프로필이 수정되었습니다.", "user": current_user}

@router.post("/refresh")
def refresh_token(refresh_token: str, response: Response, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(user.id)
    set_auth_cookies(response, new_access, refresh_token)
    return {"access_token": new_access}
