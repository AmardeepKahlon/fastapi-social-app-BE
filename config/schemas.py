from pydantic import BaseModel, NameEmail
from typing import List, Optional


class PostBase(BaseModel):
    """
    Base schema for creating a post.
    """
    content: str
    allow_comments: Optional[bool]

class PostCreate(PostBase):
    """
    Schema for creating a post.
    Inherits from PostBase.
    """
    pass

class Post(PostBase):
    """
    Schema for a post.
    Inherits from PostBase.
    Includes attributes for the post ID and owner ID.
    """
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    name: Optional[str] = None
    email: NameEmail
    
class ReceiverUser(BaseModel):
    """
    Schema for a receiver user.
    """
    id: int

class UserCreate(UserBase):
    """
    Schema for creating a user.
    Inherits from UserBase.
    """
    pass

class User(UserBase):
    """
    Schema for a user.
    Inherits from UserBase.
    Includes attributes for the user ID and list of posts.
    """
    id: int
    posts: List[Post] = []

    class Config:
        from_attributes = True
  
class Login(BaseModel):
    """
    Schema for user login data.
    """
    email: str
    password: Optional[str] = None
  
class Token(BaseModel):
    """
    Schema for authentication token.
    """
    access_token: str
    token_type: str
  
class ImageFile(BaseModel):
    """
    Schema for image file upload.
    """
    upload_file: bytes
  
class TokenBearer(BaseModel):
    """
    Schema for authentication token.
    """
    token: str
  
class TokenData(BaseModel):
    """
    Schema for token data.
    """
    email: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None
  
class CommentCreate(BaseModel):
    """
    Schema for creating a comment.
    """
    content: Optional[str] = None
    parent_comment_id: Optional[int] = None
  
class CommentApprove(BaseModel):
    """
    Schema for approving a comment.
    """
    approved_comment: Optional[bool] = None

class CommentApproveAsComment(BaseModel):
    """
    Schema for approving a comment as a comment.
    """
    content: Optional[str] = None

class LikeCreate(BaseModel):
    """
    Schema for creating a like.
    """
    pass
  
class ChatCreate(BaseModel):
    """
    Schema for creating a chat.
    """
    post_id: Optional[int] = None
    comment_id: Optional[int] = None