from sqlalchemy.orm import Session, joinedload
from db import models
from schemas.comment import CommentCreate


def create_comment(db: Session, post_id: int, user_id: int, payload: CommentCreate):
    comment = models.CommunityComment(
        post_id=post_id,
        user_id=user_id,
        content=payload.content,
        parent_id=payload.parent_id,
    )

    db.add(comment)

    # 게시글 댓글 수 증가
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    post.comment_count = (post.comment_count or 0) + 1

    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int, user_id: int):
    comment = db.query(models.CommunityComment).filter(
        models.CommunityComment.id == comment_id,
        models.CommunityComment.user_id == user_id
    ).first()

    if not comment:
        return None

    post = db.query(models.CommunityPost).filter(
        models.CommunityPost.id == comment.post_id
    ).first()

    # 자식 댓글 수 포함 재귀 삭제 개수 계산
    def count_children(node):
        return 1 + sum(count_children(child) for child in node.children)

    total = count_children(comment)

    db.delete(comment)

    post.comment_count = max((post.comment_count or 0) - total, 0)
    db.commit()

    return True


def get_comments_tree(db: Session, post_id: int):
    comments = db.query(models.CommunityComment)\
        .options(joinedload(models.CommunityComment.user))\
        .filter(models.CommunityComment.post_id == post_id)\
        .order_by(models.CommunityComment.created_at.asc())\
        .all()

    comment_map = {}
    root = []

    for c in comments:
        comment_map[c.id] = {
            "id": c.id,
            "post_id": c.post_id,
            "user_id": c.user_id,
            "content": c.content,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "user_nickname": c.user.nickname if c.user else "Unknown",
            "children": []
        }

    for c in comments:
        node = comment_map[c.id]
        if c.parent_id:
            comment_map[c.parent_id]["children"].append(node)
        else:
            root.append(node)

    return root
