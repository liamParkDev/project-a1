# routers/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_user
from schemas.product import ProductCreate, ProductUpdate
from db.crud_product import (
    create_product,
    update_product,
    delete_product,
    get_product,
    get_products_by_user,
    get_products_by_region,
    toggle_like,
)
from db.models import Product

router = APIRouter(prefix="/products", tags=["Products"])


# 상품 등록
@router.post("/")
def create(payload: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = create_product(db, current_user.id, payload)
    return {"status": "ok", "id": product.id}


# 상품 상세 조회
@router.get("/{product_id}")
def detail(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# 상품 수정
@router.put("/{product_id}")
def update(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = get_product(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    updated = update_product(db, product, payload)
    return {"status": "ok", "product": updated}


# 상품 삭제
@router.delete("/{product_id}")
def delete(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = get_product(db, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    delete_product(db, product)
    return {"status": "deleted"}


# 지역 기반 상품 목록
@router.get("/region/{region_id}")
def list_by_region(region_id: int, db: Session = Depends(get_db)):
    return get_products_by_region(db, region_id)


# 내가 올린 상품 목록
@router.get("/me")
def list_my_products(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_products_by_user(db, current_user.id)


# 좋아요 / 취소
@router.post("/{product_id}/like")
def like(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    result = toggle_like(db, current_user.id, product_id)
    return {"liked": result}
