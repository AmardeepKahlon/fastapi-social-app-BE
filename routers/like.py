from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database import get_db
from config import models
from lib import like
from lib.auth.oauth2 import get_current_user

router = APIRouter(
  prefix="/like",
  tags=["Like"]
)

@router.post("")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  '''Create like for one specific post API endpoint'''
  return like.like_post(post_id, db, current_user)

@router.get("/count")
def like_count(post_id: int, db: Session = Depends(get_db)):
  '''Get like count for one specific post API endpoint'''
  return like.like_count(post_id, db)

@router.delete("")
def unlike_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
  '''Delete like for one specific post API endpoint'''
  return like.unlike_post(post_id, db, current_user)