from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
import db.crud as crud

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        return {"status": "error", "message": "not found"}
    return product


@router.get("/search")
def search(keyword: str, db: Session = Depends(get_db)):
    return crud.search_products(db, keyword)
