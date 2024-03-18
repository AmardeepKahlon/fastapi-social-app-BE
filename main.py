from fastapi import FastAPI

from routers import auth, user

app = FastAPI()

@app.get("/api")
async def Hello():
  return {"message": "Hello"}

app.include_router(auth.router)
app.include_router(user.router)