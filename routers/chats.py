from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Chats"]
)

@router.post("/create_chat")
def create_chat(chat: schemas.ChatCreate, receiver: schemas.ReceiverUser, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_chat = models.Chat(content=chat.content, sender_id=current_user.id, receiver_id=receiver.id)
    db.add(db_chat)
    db.commit()
    return {"message": "Chat created successfully"}

@router.get("/chats")
def get_chats(db: Session = Depends(get_db)):
    return db.query(models.Chat).all()

@router.get("/chats/{chat_id}")
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    if chat := db.query(models.Chat).filter(models.Chat.id == chat_id).first():
        return chat
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")