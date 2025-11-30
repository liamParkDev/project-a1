# routers/community.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.security import get_current_user
from db.session import get_db
from db.models import User, UserRole
from db import models

import db.crud_community as crud_community
import db.crud_comment as crud_comment

from schemas.community import (
    CommunityPostCreate,
    CommunityPostUpdate,
    CommunityPostOut,
    CommunityPostListResponse,
    CommunityPostListItem,
    CommunityPostDetail
)
from schemas.comment import (
    CommentCreate,
    CommentOut,
)

router = APIRouter(
    prefix="/community",
    tags=["Community"],
)

# =====================================
# 게시글 생성
# =====================================
@router.post("/posts", response_model=CommunityPostOut)
def create_post(
    data: CommunityPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.region_id and not current_user.home_region_id:
        raise HTTPException(400, "동네가 설정되어 있지 않습니다. 먼저 GPS 인증을 해주세요.")

    post = crud_community.create_post(db, current_user, data)
    return post


# =====================================
# 게시글 상세 조회 (댓글 포함)
# =====================================
@router.get("/posts/{post_id}", response_model=CommunityPostDetail)
def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = crud_community.get_post(db, post_id)
    if not post or post.is_hidden:
        raise HTTPException(404, "Post not found")

    crud_community.increase_view_count(db, post)
    comments = crud_comment.get_comments_tree(db, post_id)

    return CommunityPostDetail(
        id=post.id,
        title=post.title,
        content=post.content,
        region_id=post.region_id,
        user_id=post.user_id,
        images=post.images,
        comments=comments,
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        created_at=post.created_at,
    )


# =====================================
# 게시글 목록
# =====================================
@router.get("/posts", response_model=CommunityPostListResponse)
def list_posts(
    page: int = 1,
    size: int = 20,
    sort: str = Query("recent", regex="^(recent|popular)$"),
    region_id: Optional[int] = None,
    my_region_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if my_region_only:
        if not current_user.home_region_id:
            raise HTTPException(400, "동네 인증이 필요합니다.")
        region_id = current_user.home_region_id

    posts, total = crud_community.list_posts(
        db, page=page, size=size, sort=sort, region_id=region_id
    )

    items = [
        CommunityPostListItem(
            id=p.id,
            title=p.title,
            region_id=p.region_id,
            user_id=p.user_id,
            like_count=p.like_count or 0,
            comment_count=p.comment_count or 0,
            view_count=p.view_count or 0,
            created_at=p.created_at,
        )
        for p in posts
    ]

    return CommunityPostListResponse(items=items, page=page, size=size, total=total)


# =====================================
# 게시글 수정
# =====================================
@router.put("/posts/{post_id}", response_model=CommunityPostOut)
def update_post(
    post_id: int,
    data: CommunityPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = crud_community.get_post(db, post_id)
    if not post or post.is_hidden:
        raise HTTPException(404, "Post not found")

    if post.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(403, "권한이 없습니다.")

    updated = crud_community.update_post(db, post, data)
    return updated


# =====================================
# 게시글 삭제
# =====================================
@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = crud_community.get_post(db, post_id)
    if not post or post.is_hidden:
        raise HTTPException(404, "Post not found")

    if post.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(403, "권한이 없습니다.")

    crud_community.soft_delete_post(db, post)
    return {"status": "ok"}


# =====================================
# 댓글 생성
# =====================================
@router.post("/posts/{post_id}/comments", response_model=CommentOut)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = crud_community.get_post(db, post_id)
    if not post:
        raise HTTPException(404, "Post not found")

    comment = crud_comment.create_comment(db, post_id, current_user.id, payload)
    comment.user_nickname = current_user.nickname
    return comment


@router.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud_community.like_post(db, current_user, post_id)
    return {"status": "ok", "liked": True}



# =====================================
# 댓글 목록 (트리)
# =====================================
@router.get("/posts/{post_id}/comments", response_model=List[CommentOut])
def list_comments(
    post_id: int,
    db: Session = Depends(get_db),
):
    return crud_comment.get_comments_tree(db, post_id)


# =====================================
# 댓글 삭제
# =====================================
@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = crud_comment.delete_comment(db, comment_id, current_user.id)
    if not ok:
        raise HTTPException(404, "Comment not found or unauthorized")
    return {"status": "ok"}


# =====================================
# 좋아요 / 좋아요 취소
# =====================================
@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    crud_community.like_post(db, current_user, post_id)
    return {"status": "ok", "liked": True}


@router.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    crud_community.unlike_post(db, current_user, post_id)
    return {"status": "ok", "liked": False}
