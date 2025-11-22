from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
import db.crud as crud
from schemas.user import UserRegister, UserLogin

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    user = crud.create_user(db, payload.email, payload.password, payload.nickname)
    return {"status": "ok", "user_id": user.id}


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        return {"status": "error", "message": "invalid credentials"}
    return {"status": "ok", "user_id": user.id, "nickname": user.nickname}
