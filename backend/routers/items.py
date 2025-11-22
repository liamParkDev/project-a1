from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.crud import create_item, get_item

router = APIRouter(prefix="/items", tags=["Items"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def new_item(name: str, db: Session = Depends(get_db)):
    return create_item(db, name)

@router.get("/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = get_item(db, item_id)
    return item or {"error": "Item not found"}
