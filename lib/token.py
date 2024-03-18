import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
from jose import JWTError, jwt

from schemas import TokenData


load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now() + timedelta(minutes=30)
  to_encode["exp"] = expire
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
      raise credentials_exception
    token_data = TokenData(email=email)
  except JWTError:
    raise credentials_exception
  return token_data