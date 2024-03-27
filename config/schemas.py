from pydantic import BaseModel
from typing import List, Optional

    
class PostBase(BaseModel):
    content: str
    allow_comments: Optional[bool]

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: Optional[str] = None
    email: str
    
class ReceiverUser(BaseModel):
    id: int

class UserCreate(UserBase):
    # password: Optional[str] = None
    pass

class User(UserBase):
    id: int
    posts: List[Post] = []

    class Config:
        from_attributes = True
  
class Login(BaseModel):
  email: str
  password: Optional[str] = None
  
class Token(BaseModel):
  access_token: str
  token_type: str
  
class ImageFile(BaseModel):
  upload_file: bytes
  
class TokenBearer(BaseModel):
  token: str
  
class TokenData(BaseModel):
  email: Optional[str] = None
  id: Optional[int] = None
  name: Optional[str] = None
  
class CommentCreate(BaseModel):
  content: Optional[str] = None
  parent_comment_id: Optional[int] = None
  
class CommentApprove(BaseModel):
  approved_comment: Optional[bool] = None
  
class LikeCreate(BaseModel):
  pass
  
class ChatCreate(BaseModel):
  post_id: Optional[int] = None
  comment_id: Optional[int] = None