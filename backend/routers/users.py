from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
import db.crud as crud

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register")
def register(email: str, password: str, nickname: str, db: Session = Depends(get_db)):
    user = crud.create_user(db, email, password, nickname)
    return {"status": "ok", "user_id": user.id}


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email, password)
    if not user:
        return {"status": "error", "message": "invalid credentials"}
    return {"status": "ok", "user_id": user.id, "nickname": user.nickname}
