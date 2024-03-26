from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, requests, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Comment"]
)

@router.post("/posts/{post_id}/comments")
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.allow_comments == False:
        approved_comment = post.user_id == current_user.id
    else: approved_comment = True
    db_comment = models.Comment(content=comment.content, approved_comment=approved_comment, user_id=current_user.id, post_id=post_id, user_name=current_user.name, time_posted=datetime.now())
    db.add(db_comment)
    db.commit()
    if post.allow_comments == False:
        comment_current = db.query(models.Comment).filter(models.Comment.user_id == current_user.id).filter(models.Comment.post_id == post_id).order_by(models.Comment.id.desc()).first()
        if comment_current.approved_comment == False:
            db_chat = models.Chat(sender_id=current_user.id, receiver_id=post.user_id, post_id=post.id, comment_id=comment_current.id, timestamp=datetime.now())
            db.add(db_chat)
            db.commit()
    return {"message": "Comment added successfully"}

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

@router.get("/parent_comment/{parent_comment_id}/comments")
def get_comment_reply(comment_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.parent_comment_id == comment_id).all()
    