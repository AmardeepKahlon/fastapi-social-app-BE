from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.models import User
from config.schemas import Login, UserCreate
from config.database import get_db
from lib.token import create_access_token
from lib.hash import Hash

router = APIRouter(
  tags=["Authentication"]
)

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if (
        user_exists := db.query(User)
        .filter(User.email == user.email)
        .first()
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user = User(email=user.email, name=user.name) #, password=Hash.bcrypt(user.password)
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}
  
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = db.query(User).filter(User.email == request.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
  # if not Hash.verify(user.password, request.password):
  #   raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")
  access_token = create_access_token(
    data = {"sub": user.email, "id": user.id}
  )
  return {"access_token": access_token, "token_type": "bearer"}