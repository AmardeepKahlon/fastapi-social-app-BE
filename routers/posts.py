from datetime import datetime
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
def get_posts(db: Session = Depends(get_db)):
    try:
        if posts := db.query(models.Post).all():
            return posts
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching posts from database",
        ) from e

# Get one specific post API endpoint
@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    if post := db.query(models.Post).filter(models.Post.id == post_id).first():
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
