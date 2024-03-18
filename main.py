from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
async def Hello():
  return {"message": "Hello"}