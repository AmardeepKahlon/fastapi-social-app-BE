from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

import cloudinary.uploader


router = APIRouter(
  tags=["Posts"]
)

@router.post("/create_post")
def create_post(title:str, content:str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = cloudinary.uploader.upload(file.file)
    print(result)
    url = result.get('secure_url')
    db_post = models.Post(title=title, content=content, user_id=current_user.id, url=url, user_name=current_user.name)
    db.add(db_post)
    db.commit()
    return {"message": "Post created successfully"}

@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()

@router.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    if post := db.query(models.Post).filter(models.Post.id == post_id).first():
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
