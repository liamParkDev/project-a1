from datetime import datetime
import enum

from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, DateTime, ForeignKey, Float,
    Enum as SAEnum
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from db.session import Base

# =====================================
# Enums
# =====================================

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class ProductCondition(enum.Enum):
    new = "new"
    used = "used"

class ProductTradeType(enum.Enum):
    direct = "direct"
    delivery = "delivery"
    both = "both"

class ProductStatus(enum.Enum):
    selling = "selling"
    reserved = "reserved"
    sold = "sold"
    hidden = "hidden"

class CategoryType(enum.Enum):
    product = "product"
    community = "community"
    both = "both"


# =====================================
# Region
# =====================================

class Region(Base):
    __tablename__ = "regions"

    id = Column(BigInteger, primary_key=True)
    country_code = Column(String(2), default="TW")
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)

    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, default=2.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="home_region")
    products = relationship("Product", back_populates="region")
    community_posts = relationship("CommunityPost", back_populates="region")


# =====================================
# User
# =====================================

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), nullable=False)
    profile_image = Column(String(500))

    role = Column(SAEnum(UserRole), default=UserRole.user)
    is_active = Column(TINYINT(1), default=1)

    refresh_token = Column(Text, nullable=True)

    home_region_id = Column(BigInteger, ForeignKey("regions.id"))
    home_lat = Column(Float)
    home_lng = Column(Float)
    gps_verified_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    home_region = relationship("Region", back_populates="users")

    # Relations
    products = relationship("Product", back_populates="seller")
    product_likes = relationship("ProductLike", back_populates="user")
    community_posts = relationship("CommunityPost", back_populates="user")
    community_comments = relationship("CommunityComment", back_populates="user")
    community_post_likes = relationship("CommunityPostLike", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="sender")


# =====================================
# Category
# =====================================

class Category(Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True)
    type = Column(SAEnum(CategoryType), default=CategoryType.product)

    parent_id = Column(BigInteger, ForeignKey("categories.id"))
    sort_order = Column(Integer, default=0)
    is_active = Column(TINYINT(1), default=1)

    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Category", remote_side=[id])

    products = relationship("Product", back_populates="category")
    community_posts = relationship("CommunityPost", back_populates="category")


# =====================================
# Product
# =====================================

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)
    seller_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    region_id = Column(BigInteger, ForeignKey("regions.id"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id"))

    title = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text)

    condition = Column(SAEnum(ProductCondition), default=ProductCondition.used)
    trade_type = Column(SAEnum(ProductTradeType), default=ProductTradeType.direct)
    status = Column(SAEnum(ProductStatus), default=ProductStatus.selling)

    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

    lat = Column(Float)
    lng = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    seller = relationship("User", back_populates="products")
    region = relationship("Region", back_populates="products")
    category = relationship("Category", back_populates="products")

    images = relationship("ProductImage", back_populates="product", cascade="all,delete-orphan")
    likes = relationship("ProductLike", back_populates="product")
    chat_rooms = relationship("ChatRoom", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    image_url = Column(String(500))
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="images")


class ProductLike(Base):
    __tablename__ = "product_likes"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    product_id = Column(BigInteger, ForeignKey("products.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="product_likes")
    product = relationship("Product", back_populates="likes")


# =====================================
# Community
# =====================================

class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    region_id = Column(BigInteger, ForeignKey("regions.id"))
    category_id = Column(BigInteger, ForeignKey("categories.id"))

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    is_hidden = Column(TINYINT(1), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="community_posts")
    region = relationship("Region", back_populates="community_posts")
    category = relationship("Category", back_populates="community_posts")

    images = relationship("CommunityPostImage", back_populates="post")
    comments = relationship("CommunityComment", back_populates="post")
    likes = relationship("CommunityPostLike", back_populates="post")


class CommunityPostImage(Base):
    __tablename__ = "community_post_images"

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("community_posts.id"))
    image_url = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("CommunityPost", back_populates="images")


class CommunityComment(Base):
    __tablename__ = "community_comments"

    id = Column(BigInteger, primary_key=True)
    post_id = Column(BigInteger, ForeignKey("community_posts.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("CommunityPost", back_populates="comments")
    user = relationship("User", back_populates="community_comments")


class CommunityPostLike(Base):
    __tablename__ = "community_post_likes"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    post_id = Column(BigInteger, ForeignKey("community_posts.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="community_post_likes")
    post = relationship("CommunityPost", back_populates="likes")


# =====================================
# Chat
# =====================================

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(BigInteger, primary_key=True)
    product_id = Column(BigInteger, ForeignKey("products.id"))
    seller_id = Column(BigInteger, ForeignKey("users.id"))
    buyer_id = Column(BigInteger, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True)
    room_id = Column(BigInteger, ForeignKey("chat_rooms.id"))
    sender_id = Column(BigInteger, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="chat_messages")
