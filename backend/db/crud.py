from sqlalchemy.orm import Session
from db import models
from core.security import hash_password, verify_password

# ----------------------
# User CRUD
# ----------------------
def create_user(db: Session, username: str, password: str):
    hashed = hash_password(password)
    user = models.User(username=username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ----------------------
# Item CRUD
# ----------------------
def create_item(db: Session, name: str):
    item = models.Item(name=name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()
