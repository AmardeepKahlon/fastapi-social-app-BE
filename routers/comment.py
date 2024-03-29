from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, requests, status
from sqlalchemy.orm import Session
from config.database import get_db
from config import models, schemas
from lib.oauth2 import get_current_user

router = APIRouter(
  tags=["Comment"]
)

# Create comment API endpoint
@router.post("/comment")
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.allow_comments == False:
        approved_comment = post.user_id == current_user.id
    else: approved_comment = True
    db_comment = models.Comment(content=comment.content, approved_comment=approved_comment, parent_comment_id=comment.parent_comment_id, user_id=current_user.id, post_id=post_id, user_name=current_user.name, time_posted=datetime.now())
    db.add(db_comment)
    db.commit()
    db_chat = None
    if not approved_comment:
        comment_current = db.query(models.Comment).filter(models.Comment.user_id == current_user.id).filter(models.Comment.post_id == post_id).order_by(models.Comment.id.desc()).first()
        if comment_current.approved_comment == False:
            db_chat = models.Chat(sender_id=current_user.id, receiver_id=post.user_id, post_id=post.id, comment_id=comment_current.id, timestamp=datetime.now())
            db.add(db_chat)
            db.commit()

        chat_created = db.query(models.Chat).filter(models.Chat.id == db_chat.id).all()

        if not chat_created:
            raise HTTPException(status_code=404, detail="Chats not created")

        response = [
            {
                "id": chat.id,
                "post_id": chat.post_id,
                "timestamp": chat.timestamp,
                "comment_id": chat.comment_id,
                "receiver": {
                    "id": chat.receiver_id
                },
                "sender": {
                    "id": chat.sender_id
                },
            }
            for chat in chat_created
        ]
        return {
            "message": "Comment added successfully",
            "chat_data": response
        }
    return {"message": "Comment added successfully"}

# Update comment through approval request API endpoint
@router.put("/comment/approve")
def comment_approve(comment_id: int, comment: schemas.CommentApprove, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db_post = db.query(models.Post).filter(models.Post.id == db_comment.post_id).first()
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to update this comment")

    if comment.approved_comment is not None:
        db_comment.approved_comment = comment.approved_comment
        
    db.commit()
    return {"message": "Comment approved successfully"}

# Create comment approval request as a comment API endpoint
@router.post("/comment/approve_as_comment")
def approve_as_comment(comment_id: int, comment: schemas.CommentApproveAsComment, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    approver_user = db.query(models.Post).filter(models.Post.id == db_comment.post_id).filter(models.Post.user_id == current_user.id).all()
    # print(approver_user)
    if not approver_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to update this comment")
    
    if comment is not None:
        approved_comment = True
        db_comment.approved_comment = True
        db_comment_reply = models.Comment(content=comment.content, approved_comment=approved_comment, parent_comment_id=db_comment.id, user_id=current_user.id, post_id=db_comment.post_id, user_name=current_user.name, time_posted=datetime.now())
        db.add(db_comment_reply)
        db.commit()
    return {"message": "Comment approved successfully"}

# Get list of all comments API endpoint
@router.get("/comments")
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * per_page

    try:
        top_level_comments = db.query(models.Comment)\
            .filter(models.Comment.post_id == post_id)\
            .filter(models.Comment.approved_comment == True)\
            .filter(models.Comment.parent_comment_id == 0)\
            .order_by(models.Comment.time_posted.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()

        for comment in top_level_comments:
            child_comments = db.query(models.Comment)\
                .filter(models.Comment.post_id == post_id)\
                .filter(models.Comment.approved_comment == True)\
                .filter(models.Comment.parent_comment_id == comment.id)\
                .all()
            comment.has_child_comments = bool(child_comments)

        return {
            "total_comments": len(top_level_comments),
            "page_loaded": page,
            "per_page": per_page,
            "comments": top_level_comments,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching comments from database",
        ) from e

# Get list of one specific comment's replies API endpoint
@router.get("/comment/reply")
def get_comment_reply(
    parent_comment_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Calculate the offset for pagination
    offset = (page - 1) * per_page

    try:
        # Query to retrieve paginated comment replies
        comments = db.query(models.Comment)\
            .filter(models.Comment.parent_comment_id == parent_comment_id)\
            .filter(models.Comment.approved_comment == True)\
            .order_by(models.Comment.time_posted.desc())\
            .offset(offset)\
            .limit(per_page)\
            .all()

        return {
            "total_comments": len(comments),
            "page_loaded": page,
            "per_page": per_page,
            "comments": comments,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching comment replies from database",
        ) from e
    