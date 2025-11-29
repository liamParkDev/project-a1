# db/crud_product.py
from sqlalchemy.orm import Session
from db.models import Product, ProductImage, ProductLike
from schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, user_id: int, payload: ProductCreate):
    product = Product(
        seller_id=user_id,
        region_id=payload.region_id,
        category_id=payload.category_id,
        title=payload.title,
        price=payload.price,
        description=payload.description,
        condition=payload.condition,
        trade_type=payload.trade_type,
        lat=payload.lat,
        lng=payload.lng,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # 이미지 생성
    for img in payload.images:
        image = ProductImage(
            product_id=product.id,
            image_url=img.image_url,
            sort_order=img.sort_order
        )
        db.add(image)

    db.commit()
    return product


def update_product(db: Session, product: Product, payload: ProductUpdate):
    for field, value in payload.dict(exclude_none=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product):
    db.delete(product)
    db.commit()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_products_by_region(db: Session, region_id: int, limit: int = 50):
    return (
        db.query(Product)
        .filter(Product.region_id == region_id)
        .order_by(Product.id.desc())
        .limit(limit)
        .all()
    )


def get_products_by_user(db: Session, user_id: int):
    return (
        db.query(Product)
        .filter(Product.seller_id == user_id)
        .order_by(Product.id.desc())
        .all()
    )


def toggle_like(db: Session, user_id: int, product_id: int):
    like = (
        db.query(ProductLike)
        .filter(ProductLike.user_id == user_id, ProductLike.product_id == product_id)
        .first()
    )

    if like:
        db.delete(like)
        db.commit()
        return False

    new_like = ProductLike(user_id=user_id, product_id=product_id)
    db.add(new_like)

    product = db.query(Product).filter(Product.id == product_id).first()
    product.like_count += 1
    db.commit()

    return True
