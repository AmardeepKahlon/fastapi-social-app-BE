from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Chats"]
)

# Create a new chat API endpoint
# @router.post("/create_chat")
# def create_chat(chat: schemas.ChatCreate, receiver: schemas.ReceiverUser, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     db_chat = models.Chat(sender_id=current_user.id, receiver_id=receiver.id, post_id=chat.post_id, comment_id=chat.comment_id, timestamp=datetime.now())
#     db.add(db_chat)
#     db.commit()
#     return {"message": "Chat created successfully"}

# Get list of all chats API endpoint
@router.get("/chats")
def get_chats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    subq = db.query(models.Chat.sender_id, models.Chat.receiver_id, func.max(models.Chat.timestamp).label("max_timestamp"))\
             .filter((models.Chat.sender_id == current_user.id) | (models.Chat.receiver_id == current_user.id))\
             .group_by(models.Chat.sender_id, models.Chat.receiver_id)\
             .subquery()

    if (
        chats := db.query(models.Chat)
        .join(
            subq,
            (models.Chat.sender_id == subq.c.sender_id)
            & (models.Chat.receiver_id == subq.c.receiver_id)
            & (models.Chat.timestamp == subq.c.max_timestamp),
        )
        .options(
            joinedload(models.Chat.sender), joinedload(models.Chat.receiver)
        )
        .all()
    ):
        return [
            {
                "id": chat.id,
                "sender": chat.sender,
                "receiver": chat.receiver,
                "timestamp": chat.timestamp,
            }
            for chat in chats
        ]
    else:
        raise HTTPException(status_code=404, detail="Chat not found")

# Get list of specific chats API endpoint
@router.get("/chats/content")
def get_chat_content(receiver_id: int, db: Session = Depends(get_db),  current_user: models.User = Depends(get_current_user)):
    if (
        chats := db.query(models.Chat)
        .filter(
            (
                (models.Chat.sender_id == current_user.id)
                & (models.Chat.receiver_id == receiver_id)
            )
            | (
                (models.Chat.sender_id == receiver_id)
                & (models.Chat.receiver_id == current_user.id)
            )
        )
        .join(models.Chat.chat_comment)
        .filter(models.Comment.approved_comment == False)
        .all()
    ):
        return [
            {
                "id": chat.id,
                "post": chat.chat_post,
                "comment": chat.chat_comment,
                "timestamp": chat.timestamp,
            }
            for chat in chats
        ]
    else:
        raise HTTPException(status_code=404, detail="Chat not found")