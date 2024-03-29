from datetime import datetime
from math import ceil
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import desc, distinct, func
from sqlalchemy.orm import Session
import cloudinary.uploader

from config import models

def create_post(allow_comments:bool, content:str, file: UploadFile, db: Session, current_user: models.User):
    try:
        result = cloudinary.uploader.upload(file.file)
        url = result.get('secure_url')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error uploading file to cloudinary",
        ) from e

    try:
        db_post = models.Post(allow_comments=allow_comments, content=content, user_id=current_user.id, url=url, user_name=current_user.name, post_time=datetime.now())
        db.add(db_post)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating post in database",
        ) from e

    return {"message": "Post created successfully"}
  
def get_posts(
    page,
    per_page,
    db: Session
):
    offset = (page - 1) * per_page

    try:
        if (
            posts_with_counts := db.query(
                models.Post,
                func.count(distinct(models.Like.id)).label("like_count"),
                func.count(distinct(models.Comment.id)).label("comment_count"),
            )
            .outerjoin(models.Like, models.Post.id == models.Like.post_id)
            .outerjoin(
                models.Comment, models.Post.id == models.Comment.post_id
            )
            .group_by(models.Post.id)
            .order_by(desc(models.Post.post_time))
            .offset(offset)
            .limit(per_page)
            .all()
        ):
            total_posts = db.query(models.Post).count()

            total_pages = ceil(total_posts / per_page)

            posts = [
                {
                    "post": post,
                    "like_count": like_count,
                    "comment_count": comment_count
                }
                for post, like_count, comment_count in posts_with_counts
            ]
            return {
                "total_posts": len(posts),
                "total_pages": total_pages,
                "page_loaded": page,
                "per_page": per_page,
                "posts": posts
            }
        else:
            raise HTTPException(status_code=404, detail="No posts found")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching posts from database",
        ) from e
        
def get_post(post_id, db: Session):
    try:
        post_with_counts = db.query(
            models.Post,
            func.count(distinct(models.Like.id)),
            func.count(distinct(models.Comment.id))
        ) \
            .outerjoin(models.Like, models.Post.id == models.Like.post_id) \
            .outerjoin(models.Comment, models.Post.id == models.Comment.post_id) \
            .filter(models.Post.id == post_id) \
            .group_by(models.Post.id) \
            .first()

        if not post_with_counts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        post, like_count, comment_count = post_with_counts

        return {
            "post": post,
            "like_count": like_count,
            "comment_count": comment_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching post from database",
        ) from e