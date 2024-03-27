from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Chats"]
)

# Create a new chat API endpoint
@router.post("/create_chat")
def create_chat(chat: schemas.ChatCreate, receiver: schemas.ReceiverUser, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_chat = models.Chat(sender_id=current_user.id, receiver_id=receiver.id, post_id=chat.post_id, comment_id=chat.comment_id, timestamp=datetime.now())
    db.add(db_chat)
    db.commit()
    return {"message": "Chat created successfully"}

# Get list of all chats API endpoint
@router.get("/chats")
def get_chats(db: Session = Depends(get_db)):
    return db.query(models.Chat).all()

@router.get("/chats/{sender_id}")
def get_chats(sender_id: int, db: Session = Depends(get_db)):
    if chat := db.query(models.Chat).filter(models.Chat.sender_id == sender_id).order_by(models.Chat.id.desc()).first():
        return chat
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

# Get list of specific chats API endpoint
@router.get("/chats/{sender_id}&{receiver_id}")
def get_chat(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    if chat := db.query(models.Chat).filter(models.Chat.sender_id == sender_id).filter(models.Chat.receiver_id == receiver_id).all():
        return chat
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")