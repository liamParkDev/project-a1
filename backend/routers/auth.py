from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    create_oauth_state,
    verify_oauth_state,
    set_auth_cookies,
    get_current_user,
)
from db.session import get_db
from db import crud
from db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


OAUTH_PROVIDERS = {"google", "line"}


class OAuthLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    profile_complete: bool


class CompleteProfileRequest(BaseModel):
    nickname: str | None = None
    profile_image: str | None = None


def _get_redirect_uri(provider: str) -> str:
    return f"{settings.OAUTH_REDIRECT_BASE}/{provider}/callback"


def _validate_provider_config(provider: str):
    if provider == "google":
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth is not configured")
    elif provider == "line":
        if not settings.LINE_CLIENT_ID or not settings.LINE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="LINE OAuth is not configured")
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")


def _build_google_auth_url(state: str, redirect_uri: str) -> str:
    scope = "openid email profile"
    return (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code&scope={scope}&state={state}"
        "&access_type=offline&prompt=consent"
    )


def _build_line_auth_url(state: str, redirect_uri: str) -> str:
    scope = "openid email profile"
    return (
        "https://access.line.me/oauth2/v2.1/authorize"
        f"?response_type=code&client_id={settings.LINE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&scope={scope}"
    )


def _build_auth_url(provider: str, state: str, redirect_uri: str) -> str:
    if provider == "google":
        return _build_google_auth_url(state, redirect_uri)
    if provider == "line":
        return _build_line_auth_url(state, redirect_uri)
    raise HTTPException(status_code=400, detail="Unsupported provider")


async def _exchange_google_token(code: str, redirect_uri: str) -> dict:
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://oauth2.googleapis.com/token", data=data)
        token_resp.raise_for_status()
        token_json = token_resp.json()

        userinfo_resp = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {token_json['access_token']}"},
        )
        userinfo_resp.raise_for_status()
        userinfo = userinfo_resp.json()

    return {
        "provider_user_id": userinfo.get("sub"),
        "email": userinfo.get("email"),
        "nickname": userinfo.get("name"),
    }


async def _exchange_line_token(code: str, redirect_uri: str) -> dict:
    data = {
        "code": code,
        "client_id": settings.LINE_CLIENT_ID,
        "client_secret": settings.LINE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_resp.raise_for_status()
        token_json = token_resp.json()

        profile_resp = await client.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {token_json['access_token']}"},
        )
        profile_resp.raise_for_status()
        profile = profile_resp.json()

    return {
        "provider_user_id": profile.get("userId"),
        "email": token_json.get("email"),  # 이메일을 scope에서 허용한 경우에만 반환
        "nickname": profile.get("displayName"),
    }


async def _fetch_provider_profile(provider: str, code: str, redirect_uri: str) -> dict:
    if provider == "google":
        return await _exchange_google_token(code, redirect_uri)
    if provider == "line":
        return await _exchange_line_token(code, redirect_uri)
    raise HTTPException(status_code=400, detail="Unsupported provider")


def _issue_tokens(
    response: Response,
    user: User,
    db: Session,
    redirect_url: str | None = None,
):
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.refresh_token = refresh_token
    user.last_login = datetime.utcnow()
    db.commit()

    if redirect_url:
        redirect = RedirectResponse(url=redirect_url)
        set_auth_cookies(redirect, access_token, refresh_token)
        return redirect

    set_auth_cookies(response, access_token, refresh_token)
    return OAuthLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        profile_complete=bool(user.profile_complete),
    )


def _handle_email_conflict(db: Session, email: str):
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        return
    if existing.password_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="EMAIL_IN_USE",
        )


@router.get("/{provider}/login")
async def oauth_login(provider: str, redirect: str | None = Query(default=None)):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    _validate_provider_config(provider)
    redirect_uri = _get_redirect_uri(provider)
    state = create_oauth_state(provider, redirect)
    auth_url = _build_auth_url(provider, state, redirect_uri)
    return {"auth_url": auth_url, "state": state}


@router.get("/{provider}/callback", response_model=OAuthLoginResponse)
async def oauth_callback(
    provider: str,
    request: Request,
    response: Response,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    _validate_provider_config(provider)

    payload = verify_oauth_state(state)
    if payload.get("sub") != provider:
        raise HTTPException(status_code=400, detail="State mismatch")

    redirect_uri = _get_redirect_uri(provider)
    profile = await _fetch_provider_profile(provider, code, redirect_uri)
    provider_user_id = profile.get("provider_user_id")
    email = profile.get("email")
    nickname = profile.get("nickname")

    if not provider_user_id:
        raise HTTPException(status_code=400, detail="Missing provider user id")

    user = crud.get_user_by_provider(db, provider, provider_user_id)
    if not user:
        if email:
            _handle_email_conflict(db, email)
        user = crud.create_oauth_user(
            db=db,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
            nickname=nickname,
            profile_complete=False,
        )

    redirect_target = payload.get("redirect")
    return _issue_tokens(response, user, db, redirect_url=redirect_target)


@router.post("/complete-profile", response_model=OAuthLoginResponse)
def complete_profile(
    payload: CompleteProfileRequest,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.nickname:
        current_user.nickname = payload.nickname
    if payload.profile_image:
        current_user.profile_image = payload.profile_image
    current_user.profile_complete = 1
    db.commit()
    db.refresh(current_user)

    return _issue_tokens(response, current_user, db)


@router.post("/connect/{provider}", response_model=OAuthLoginResponse)
async def connect_provider(
    provider: str,
    response: Response,
    code: str,
    state: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    _validate_provider_config(provider)
    payload = verify_oauth_state(state)
    if payload.get("sub") != provider:
        raise HTTPException(status_code=400, detail="State mismatch")
    redirect_uri = _get_redirect_uri(provider)
    profile = await _fetch_provider_profile(provider, code, redirect_uri)
    provider_user_id = profile.get("provider_user_id")
    email = profile.get("email")

    try:
        crud.link_provider_to_user(
            db=db,
            user=current_user,
            provider=provider,
            provider_user_id=provider_user_id,
            email=email,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return _issue_tokens(response, current_user, db)


@router.post("/disconnect/{provider}")
def disconnect_provider(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    try:
        crud.disconnect_provider(db, current_user, provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"message": "disconnected"}
