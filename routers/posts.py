from datetime import datetime
from math import ceil
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import desc, distinct, func
from sqlalchemy.orm import Session
import cloudinary.uploader

from config.database import get_db
from config import models, schemas
from lib.auth.oauth2 import get_current_user
from lib import posts

router = APIRouter(
  prefix="/posts",
  tags=["Posts"]
)

@router.post("")
def create_post(allow_comments:bool, content:str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  '''Create a new post API endpoint'''
  return posts.create_post(allow_comments, content, file, db, current_user)


@router.get("")
def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
  '''Get all posts API endpoint'''
  return posts.get_posts(page, per_page, db)

@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
  '''Get one specific post API endpoint'''
  return posts.get_post(post_id, db)
