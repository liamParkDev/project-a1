from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from db.session import get_db
from db import models
from db.models import User, UserRole

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=102400,
    argon2__parallelism=8,
    argon2__time_cost=3,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return hash_password(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

def _create_token(data: dict, expires_minutes: int) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def create_access_token(user_id: int, expires_minutes: int = 60) -> str:
    return _create_token({"sub": str(user_id), "type": "access"}, expires_minutes)


def create_refresh_token(user_id: int, expires_minutes: int = 60 * 24 * 7) -> str:
    return _create_token({"sub": str(user_id), "type": "refresh"}, expires_minutes)


def create_oauth_state(provider: str, redirect_path: str | None = None, expires_minutes: int = 10) -> str:
    payload = {"sub": provider, "type": "oauth_state"}
    if redirect_path:
        payload["redirect"] = redirect_path
    return _create_token(payload, expires_minutes)


def verify_oauth_state(state: str) -> dict:
    payload = decode_token(state)
    if payload.get("type") != "oauth_state":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    return payload


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active or user.deleted_at:
        raise HTTPException(status_code=403, detail="Inactive user")
    if user.suspended_until and user.suspended_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="User suspended")

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str | None = None,
    access_expires_minutes: int = 60,
    refresh_expires_minutes: int = 60 * 24 * 7,
):
    """
    JWT를 쿠키로 내려주는 헬퍼 (웹 클라이언트용)
    """
    access_expires = access_expires_minutes * 60
    refresh_expires = refresh_expires_minutes * 60
    response.set_cookie(
        "access_token",
        access_token,
        max_age=access_expires,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
    )
    if refresh_token:
        response.set_cookie(
            "refresh_token",
            refresh_token,
            max_age=refresh_expires,
            secure=True,
            httponly=True,
            samesite="lax",
            path="/",
        )
