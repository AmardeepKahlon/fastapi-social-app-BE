from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

import cloudinary.uploader


router = APIRouter(
  tags=["Posts"]
)

# Create a new post API endpoint
@router.post("/create_post")
def create_post(allow_comments:bool, content:str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        result = cloudinary.uploader.upload(file.file)
        url = result.get('secure_url')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file to cloudinary",
        ) from e

    try:
        db_post = models.Post(allow_comments=allow_comments, content=content, user_id=current_user.id, url=url, user_name=current_user.name, post_time=datetime.now())
        db.add(db_post)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post in database",
        ) from e

    return {"message": "Post created successfully"}

# Get all posts API endpoint
@router.get("/posts")
def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page

    try:
        if (
            posts_with_likes := db.query(
                models.Post, func.count(models.Like.id)
            )
            .outerjoin(models.Like, models.Post.id == models.Like.post_id)
            .group_by(models.Post.id)
            .order_by(desc(models.Post.post_time))
            .offset(offset)
            .limit(per_page)
            .all()
        ):
            posts = [
                    {"post": post, "like_count": like_count}
                    for post, like_count in posts_with_likes
                ]
            return {
                "total_posts": len(posts),
                "pages_loaded": page,
                "per_page": per_page,
                "posts": posts
            }
        else:
            raise HTTPException(status_code=404, detail="No posts found")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching posts from database",
        ) from e

# Get one specific post API endpoint
@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    try:
        post_with_likes = db.query(models.Post, func.count(models.Like.id))\
            .outerjoin(models.Like, models.Post.id == models.Like.post_id)\
            .filter(models.Post.id == post_id)\
            .group_by(models.Post.id)\
            .first()

        if not post_with_likes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        post, like_count = post_with_likes

        return {"post": post, "like_count": like_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching post from database",
        ) from e
