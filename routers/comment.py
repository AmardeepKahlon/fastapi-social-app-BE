from datetime import datetime
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, requests, status
from sqlalchemy.orm import Session

from config.database import get_db
from config import models, schemas
from lib.auth.oauth2 import get_current_user
from lib import comments

router = APIRouter(
  prefix="/comments",
  tags=["Comments"]
)

# Create comment API endpoint
@router.post("")
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return comments.add_comment(post_id, comment, db, current_user)

# Update comment through approval request API endpoint
@router.put("/approve")
def comment_approve(comment_id: int, comment: schemas.CommentApprove, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return comments.comment_approve(comment_id, comment, db, current_user)

# Create comment approval request as a comment API endpoint
@router.post("/approve_as_comment", )
def approve_as_comment(comment_id: int, comment: schemas.CommentApproveAsComment, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return comments.approve_as_comment(comment_id, comment, db, current_user)

# Get list of all comments API endpoint
@router.get("")
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return comments.get_comments(post_id, page, per_page, db)

# Get list of one specific comment's replies API endpoint
@router.get("/reply")
def get_comment_reply(
    parent_comment_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return comments.get_comment_reply(parent_comment_id, page, per_page, db)
    