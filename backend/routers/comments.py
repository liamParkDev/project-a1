from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import User
from core.security import get_current_user

from schemas.comment import CommentCreate, CommentOut
import db.crud_comment as crud_comment

router = APIRouter(prefix="/community/comments", tags=["Comments"])


# ------------------------
# 댓글 생성
# ------------------------
@router.post("/{post_id}", response_model=CommentOut)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = crud_comment.create_comment(
        db, post_id, current_user.id, payload
    )

    # 응답에 nickname 포함시키기
    comment.user_nickname = current_user.nickname
    return comment


# ------------------------
# 댓글 삭제
# ------------------------
@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ok = crud_comment.delete_comment(db, comment_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")

    return {"status": "ok"}


# ------------------------
# 댓글 트리 조회
# ------------------------
@router.get("/post/{post_id}", response_model=list[CommentOut])
def read_comments(
    post_id: int,
    db: Session = Depends(get_db),
):
    comments = crud_comment.get_comments_tree(db, post_id)
    return comments
