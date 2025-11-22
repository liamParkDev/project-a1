from sqlalchemy.orm import Session
from db import models
from core.security import hash_password, verify_password


# ===== USERS =====

def create_user(db: Session, email: str, password: str, nickname: str):
    hashed = hash_password(password)  # Argon2 해싱
    user = models.User(email=email, password_hash=hashed, nickname=nickname)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):  # Argon2 검증
        return None
    return user


# ===== PRODUCTS =====

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def search_products(db: Session, keyword: str):
    return (
        db.query(models.Product)
        .filter(models.Product.name_ko.like(f"%{keyword}%"))
        .all()
    )


# ===== TRANSLATION QUEUE =====

def add_translate_job(db: Session, source_text: str, source_lang: str, target_lang: str):
    job = models.TranslateQueue(
        source_text=source_text,
        source_lang=source_lang,
        target_lang=target_lang,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
