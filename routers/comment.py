from fastapi import APIRouter, Depends, HTTPException, status
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
    db_comment = models.Comment(content=comment.content, user_id=current_user.id, post_id=post_id)
    db.add(db_comment)
    db.commit()
    return {"message": "Comment added successfully"}

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()