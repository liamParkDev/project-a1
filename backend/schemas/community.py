from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# ===============================
# 이미지
# ===============================

class CommunityPostImageOut(BaseModel):
    id: int
    image_url: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ===============================
# 댓글
# ===============================

class CommentOut(BaseModel):
    id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    children: List["CommentOut"] = []

    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None


# ===============================
# 게시글 생성/수정
# ===============================

class CommunityPostCreate(BaseModel):
    title: str
    content: str
    region_id: Optional[int] = None
    image_urls: Optional[List[str]] = None


class CommunityPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_urls: Optional[List[str]] = None


# ===============================
# 게시글 기본 출력
# ===============================

class CommunityPostOut(BaseModel):
    id: int
    title: str
    content: str
    region_id: int
    category_id: Optional[int] = None
    user_id: int
    view_count: int
    like_count: int
    comment_count: int
    is_hidden: int
    created_at: datetime
    images: List[CommunityPostImageOut]

    model_config = {"from_attributes": True}


# ===============================
# 게시글 목록용
# ===============================

class CommunityPostListItem(BaseModel):
    id: int
    title: str
    region_id: int
    user_id: int
    like_count: int
    comment_count: int
    view_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CommunityPostListResponse(BaseModel):
    items: List[CommunityPostListItem]
    page: int
    size: int
    total: int


# ===============================
# 게시글 상세 (댓글 포함)
# ===============================

class CommunityPostDetail(BaseModel):
    id: int
    title: str
    content: str
    region_id: int
    user_id: int
    images: List[CommunityPostImageOut]
    comments: List[CommentOut]
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
