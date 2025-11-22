from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT, DECIMAL
from datetime import datetime
from db.session import Base
import enum



class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    is_active = Column(TINYINT(1), default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    reviews = relationship("Review", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    name_ko = Column(String(255), nullable=False)
    name_en = Column(String(255))
    brand = Column(String(255))
    category = Column(String(255))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    ingredients = relationship("ProductIngredient", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    bookmarks = relationship("Bookmark", back_populates="product")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(BigInteger, primary_key=True)
    name_ko = Column(String(255), nullable=False)
    name_en = Column(String(255))
    name_cn = Column(String(255))
    ewg_score = Column(TINYINT)
    description_ko = Column(Text)
    description_en = Column(Text)
    description_cn = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("ProductIngredient", back_populates="ingredient")


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"

    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"))
    ingredient_id = Column(BigInteger, ForeignKey("ingredients.id", ondelete="CASCADE"))
    percentage = Column(DECIMAL(5, 2))

    product = relationship("Product", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="products")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"))
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    rating = Column(TINYINT, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(BigInteger, ForeignKey("products.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    product = relationship("Product", back_populates="bookmarks")


class TranslateQueue(Base):
    __tablename__ = "translate_queue"

    id = Column(BigInteger, primary_key=True)
    source_text = Column(Text, nullable=False)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    status = Column(Enum("pending", "processing", "done", "error"), default="pending")
    result_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
