import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from config import models
from config.database import get_db
from config.schemas import TokenData




load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now() + timedelta(minutes=30)
  to_encode["exp"] = expire
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception):
  # sourcery skip: avoid-builtin-shadow
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # print(payload)
    email: str = payload.get("sub")
    if email is None:
      raise credentials_exception
    name: str = payload.get("name")
    id: int = payload.get("id")
    token_data = TokenData(email=email, id=id, name=name)
  except JWTError as e:
    raise credentials_exception from e
  return token_data