# db/crud_community.py
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from db import models
from schemas.community import (
    CommunityPostCreate,
    CommunityPostUpdate,
)


# =========================
# 게시글 CRUD
# =========================

def create_post(
    db: Session,
    *,
    user: models.User,
    data: CommunityPostCreate,
) -> models.CommunityPost:
    # region_id 없으면 유저의 home_region 사용
    region_id = data.region_id or user.home_region_id

    post = models.CommunityPost(
        user_id=user.id,
        region_id=region_id,
        category_id=data.category_id,
        title=data.title,
        content=data.content,
    )
    db.add(post)
    db.flush()  # post.id 생성용

    # 이미지가 있으면 저장
    if data.image_urls:
        for idx, url in enumerate(data.image_urls):
            img = models.CommunityPostImage(
                post_id=post.id,
                image_url=url,
                # sort_order가 모델에 없으면 이 줄 삭제
                # sort_order=idx,
            )
            db.add(img)

    db.commit()
    db.refresh(post)
    return post


def get_post(db: Session, post_id: int) -> Optional[models.CommunityPost]:
    return (
        db.query(models.CommunityPost)
        .filter(models.CommunityPost.id == post_id)
        .first()
    )


def list_posts(
    db: Session,
    *,
    page: int,
    size: int,
    sort: str = "recent",
    region_id: Optional[int] = None,
) -> Tuple[List[models.CommunityPost], int]:
    """
    sort: recent | popular
    """
    q = db.query(models.CommunityPost).filter(models.CommunityPost.is_hidden == 0)

    if region_id:
        q = q.filter(models.CommunityPost.region_id == region_id)

    total = q.count()

    if sort == "popular":
        q = q.order_by(
            models.CommunityPost.like_count.desc(),
            models.CommunityPost.id.desc(),
        )
    else:  # recent
        q = q.order_by(models.CommunityPost.created_at.desc())

    items = q.offset((page - 1) * size).limit(size).all()
    return items, total


def update_post(
    db: Session,
    *,
    post: models.CommunityPost,
    data: CommunityPostUpdate,
):
    if data.title is not None:
        post.title = data.title
    if data.content is not None:
        post.content = data.content
    if data.is_hidden is not None:
        post.is_hidden = 1 if data.is_hidden else 0

    # 이미지 전체 교체 (옵션)
    if data.image_urls is not None:
        # 기존 이미지 삭제
        db.query(models.CommunityPostImage).filter(
            models.CommunityPostImage.post_id == post.id
        ).delete()
        # 새로 추가
        for idx, url in enumerate(data.image_urls):
            img = models.CommunityPostImage(
                post_id=post.id,
                image_url=url,
                # sort_order=idx,
            )
            db.add(img)

    db.commit()
    db.refresh(post)
    return post


def soft_delete_post(
    db: Session,
    *,
    post: models.CommunityPost,
):
    post.is_hidden = 1
    db.commit()
    db.refresh(post)
    return post


def increase_view_count(db: Session, post: models.CommunityPost):
    post.view_count = (post.view_count or 0) + 1
    db.commit()
    db.refresh(post)
    return post


# =========================
# 댓글
# =========================

def create_comment(
    db: Session,
    *,
    user: models.User,
    post: models.CommunityPost,
    content: str,
) -> models.CommunityComment:
    comment = models.CommunityComment(
        post_id=post.id,
        user_id=user.id,
        content=content,
    )
    db.add(comment)

    # 댓글 수 증가
    post.comment_count = (post.comment_count or 0) + 1

    db.commit()
    db.refresh(comment)
    return comment


def list_comments(
    db: Session,
    post_id: int,
) -> List[models.CommunityComment]:
    return (
        db.query(models.CommunityComment)
        .filter(models.CommunityComment.post_id == post_id)
        .order_by(models.CommunityComment.created_at.asc())
        .all()
    )


def delete_comment(
    db: Session,
    *,
    comment: models.CommunityComment,
):
    # 댓글 수 감소
    post = (
        db.query(models.CommunityPost)
        .filter(models.CommunityPost.id == comment.post_id)
        .first()
    )
    if post and post.comment_count and post.comment_count > 0:
        post.comment_count -= 1

    db.delete(comment)
    db.commit()


# =========================
# 좋아요
# =========================

def get_post_like(
    db: Session,
    *,
    user_id: int,
    post_id: int,
) -> Optional[models.CommunityPostLike]:
    return (
        db.query(models.CommunityPostLike)
        .filter(
            models.CommunityPostLike.user_id == user_id,
            models.CommunityPostLike.post_id == post_id,
        )
        .first()
    )

def like_post(db: Session, user: models.User, post_id: int):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        return None

    exists = db.query(models.CommunityPostLike).filter(
        models.CommunityPostLike.user_id == user.id,
        models.CommunityPostLike.post_id == post_id
    ).first()

    if exists:
        return exists

    like = models.CommunityPostLike(user_id=user.id, post_id=post_id)
    db.add(like)

    post.like_count = (post.like_count or 0) + 1

    db.commit()
    return like


def unlike_post(db: Session, user: models.User, post_id: int):
    like = db.query(models.CommunityPostLike).filter(
        models.CommunityPostLike.user_id == user.id,
        models.CommunityPostLike.post_id == post_id
    ).first()

    if not like:
        return

    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()

    db.delete(like)

    if post.like_count:
        post.like_count -= 1

    db.commit()
