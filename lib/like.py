from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from config import models

def like_post(post_id: int, db: Session, current_user: models.User):
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

def like_count(post_id: int, db: Session):
    like_count = db.query(models.Like).filter(models.Like.post_id == post_id).count()
    return {"like_count": like_count}

def unlike_post(post_id, db: Session, current_user: models.User):
    like = db.query(models.Like).filter(models.Like.user_id == current_user.id, models.Like.post_id == post_id).first()
    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like not found")
    db.delete(like)
    db.commit()
    return {"message": "Post unliked successfully"}