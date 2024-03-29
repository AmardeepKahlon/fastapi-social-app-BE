from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Union, cast

from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing_extensions import Annotated, Doc  # typ
from config import models
from config.models import User
from config.schemas import Login, UserCreate
from config.database import get_db
from lib.auth.token import create_access_token
from lib.auth.hash import Hash
from lib.auth.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
  tags=["Authentication"]
)

revoked_tokens = set()

# Register user API endpoint
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # print(user.email.name)
    if not user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")
    if not user.name or user.name == "":
        user.name = user.email.name
    elif not user.name.strip() or user.name.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid name")

    if (
        user_exists := db.query(models.User)
        .filter(models.User.email == user.email.email)
        .first()
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user = models.User(email=user.email.email, name=user.name)
    db.add(db_user)
    db.commit()
    return {"message": "User created successfully"}

# Login user API endpoint
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user = db.query(User).filter(User.email == request.username).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
  # if not Hash.verify(user.password, request.password):
  #   raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials!")
  access_token = create_access_token(
    data = {"sub": user.email, "id": user.id, "name": user.name}
  )
  return {
    "access_token": access_token,
    "token_type": "bearer",
    "user_name": user.name,
    "user_id": user.id
  }
  
# Logout user API endpoint
@router.post("/logout")
def logout(access_token: str, db: Session = Depends(get_db)):
    if access_token in revoked_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already revoked")
    revoked_tokens.add(access_token)
    return {"message": "Logout successful"}