from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, posts, comment, like, chats
from config.database import engine
from config import models

app = FastAPI()

models.Base.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(chats.router)

@app.get("/api")
async def Hello():
  return {"message": "Hello"}

# app.include_router(user.router)