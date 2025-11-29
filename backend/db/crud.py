# db/crud.py
from sqlalchemy.orm import Session
from core.security import hash_password, verify_password
from db.models import User, Product


# =======================================
# USERS
# =======================================

def create_user(db: Session, email: str, password: str, nickname: str):
    """
    회원가입: User 생성
    """
    hashed = hash_password(password)
    user = User(
        email=email,
        password_hash=hashed,
        nickname=nickname,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    """
    로그인: 이메일/비밀번호 검증
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# =======================================
# PRODUCTS
# =======================================

def get_product(db: Session, product_id: int):
    """
    상품 1개 조회
    """
    return db.query(Product).filter(Product.id == product_id).first()


def search_products(db: Session, keyword: str):
    """
    상품 검색 (title LIKE 검색)
    """
    q = f"%{keyword}%"
    return db.query(Product).filter(Product.title.like(q)).all()


# =======================================
# (선택) Product 생성/수정/삭제도 여기에 추가 예정
# =======================================

def create_product(db: Session, seller_id: int, title: str, price: int, description: str = None):
    """
    상품 등록
    """
    product = Product(
        seller_id=seller_id,
        title=title,
        price=price,
        description=description
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
