from datetime import datetime
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from config.database import get_db
from config import models, schemas
from lib.auth.oauth2 import get_current_user
from lib import chats

router = APIRouter(
  prefix="/chats",
  tags=["Chats"]
)

# Create a new chat API endpoint
'''
@router.post("")
def create_chat(chat: schemas.ChatCreate, receiver: schemas.ReceiverUser, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_chat = models.Chat(sender_id=current_user.id, receiver_id=receiver.id, post_id=chat.post_id, comment_id=chat.comment_id, timestamp=datetime.now())
    db.add(db_chat)
    db.commit()
    return {"message": "Chat created successfully"}
'''

# Get list of all chats API endpoint
@router.get("")
def get_chats(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return chats.get_chats(page, per_page, db, current_user)

# Get list of specific chats API endpoint
@router.get("/content")
def get_chat_content(
    receiver_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return chats.get_chat_content(receiver_id, page, per_page, db, current_user)