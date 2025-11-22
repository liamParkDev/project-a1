from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.crud import create_user

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    return create_user(db, username, password)
