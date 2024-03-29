from datetime import datetime
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
def get_chats(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    offset = (page - 1) * per_page

    subq = db.query(
        models.Chat.sender_id,
        models.Chat.receiver_id,
        func.max(models.Chat.timestamp).label("max_timestamp")
    )\
        .filter(
            (models.Chat.sender_id == current_user.id) | (models.Chat.receiver_id == current_user.id)
        )\
        .group_by(models.Chat.sender_id, models.Chat.receiver_id)\
        .subquery()

    total_chats = db.query(models.Chat)\
        .join(
            subq,
            (models.Chat.sender_id == subq.c.sender_id)
            & (models.Chat.receiver_id == subq.c.receiver_id)
            & (models.Chat.timestamp == subq.c.max_timestamp),
        )\
        .count()

    total_pages = ceil(total_chats / per_page)
    
    if (
        chats := db.query(models.Chat)
        .join(
            subq,
            (models.Chat.sender_id == subq.c.sender_id)
            & (models.Chat.receiver_id == subq.c.receiver_id)
            & (models.Chat.timestamp == subq.c.max_timestamp),
        )
        .order_by(models.Chat.timestamp.desc())
        .offset(offset)
        .limit(per_page)
        .options(
            joinedload(models.Chat.sender), joinedload(models.Chat.receiver)
        )
        .all()
    ):
        chats = [
                {
                    "id": chat.id,
                    "sender": chat.sender,
                    "receiver": chat.receiver,
                    "timestamp": chat.timestamp,
                }
                for chat in chats
            ]
        return {
            "total_chats": len(chats),
            "total_pages": total_pages,
            "page_loaded": page,
            "per_page": per_page,
            "chats": chats
        }
    else:
        raise HTTPException(status_code=404, detail="No chats found")

# Get list of specific chats API endpoint
@router.get("/chats/content")
def get_chat_content(
    receiver_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    all_chats = []

    offset = (page - 1) * per_page

    query = db.query(models.Chat)\
        .filter(
            (
                (models.Chat.sender_id == current_user.id)
                & (models.Chat.receiver_id == receiver_id)
            )
            | (
                (models.Chat.sender_id == receiver_id)
                & (models.Chat.receiver_id == current_user.id)
            )
        )\
        .join(models.Chat.chat_comment)\
        .filter(models.Comment.approved_comment == False)\
        .order_by(models.Comment.time_posted.desc())\
        .offset(offset)\
        .limit(per_page)\
        .all()

    all_chats.extend(query)

    total_chats = db.query(models.Chat)\
        .filter(
            (
                (models.Chat.sender_id == current_user.id)
                & (models.Chat.receiver_id == receiver_id)
            )
            | (
                (models.Chat.sender_id == receiver_id)
                & (models.Chat.receiver_id == current_user.id)
            )
        )\
        .join(models.Chat.chat_comment)\
        .filter(models.Comment.approved_comment == False)\
        .count()

    total_pages = ceil(total_chats / per_page)
    
    if not all_chats:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {
        "total_chats": len(all_chats),
        "toatal_pages": total_pages,
        "page_loaded": page,
        "per_page": per_page,
        "chats": [
            {
                "id": chat.id,
                "post": chat.chat_post,
                "comment": chat.chat_comment,
                "timestamp": chat.timestamp,
            }
            for chat in all_chats
        ]
    }