from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, posts, comment, like, chats
from config.database import engine
from config import models

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# models.Base.metadata.create_all(engine)

import cloudinary

'''cloudinary configration to upload images'''
cloudinary.config( 
  cloud_name = os.getenv('CLOUD_NAME'), 
  api_key = os.getenv('API_KEY'),
  api_secret = os.getenv('API_SECRET') 
)

'''App middleware'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

'''App routes'''
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(chats.router)
# app.include_router(user.router)