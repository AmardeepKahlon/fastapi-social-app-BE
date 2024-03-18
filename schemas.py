from pydantic import BaseModel
from typing import List, Optional

    
class User(BaseModel):
  name: Optional[str] = None
  email: str
  password: str
  
class Login(BaseModel):
  username: str
  password: str
  
class Token(BaseModel):
  access_token: str
  token_type: str
  
class TokenData(BaseModel):
  email: Optional[str] = None