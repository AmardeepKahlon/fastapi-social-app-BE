from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from models.user import User
from database import get_db
from lib.token import create_access_token

router = APIRouter(
  tags=["Authentication"]
)

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = db.query(User).filter(User.email == request.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
  if not hash.Hash.verify(user.password, request.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")
  access_token = create_access_token(
    data = {"sub": user.email}
  )
  return {"access_token": access_token, "token_type": "bearer"}