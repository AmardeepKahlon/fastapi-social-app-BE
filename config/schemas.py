from pydantic import BaseModel
from typing import List, Optional

    
class PostBase(BaseModel):
    title: str
    content: str

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

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    posts: List[Post] = []

    class Config:
        from_attributes = True
  
class Login(BaseModel):
  email: str
  password: str
  
class Token(BaseModel):
  access_token: str
  token_type: str
  
class TokenData(BaseModel):
  email: Optional[str] = None
  id: Optional[int] = None
  
class CommentCreate(BaseModel):
    content: str

class LikeCreate(BaseModel):
    pass