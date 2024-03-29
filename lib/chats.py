from math import ceil
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from config import models

def get_chats(
    page,
    per_page,
    db: Session,
    current_user: models.User
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
      
def get_chat_content(
    receiver_id: int,
    page,
    per_page,
    db: Session,
    current_user: models.User
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