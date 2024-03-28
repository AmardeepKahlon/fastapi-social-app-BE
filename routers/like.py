from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Like"]
)

@router.post("/like")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if (
        existing_like := db.query(models.Like)
        .filter(
            models.Like.user_id == current_user.id,
            models.Like.post_id == post_id,
        )
        .first()
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already liked this post")
    like = models.Like(user_id=current_user.id, post_id=post_id)
    db.add(like)
    db.commit()
    return {"message": "Post liked successfully"}

@router.get("/like/count")
def get_like_count(post_id: int, db: Session = Depends(get_db)):
    like_count = db.query(models.Like).filter(models.Like.post_id == post_id).count()
    return {"like_count": like_count}

@router.delete("/like")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    like = db.query(models.Like).filter(models.Like.user_id == current_user.id, models.Like.post_id == post_id).first()
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}