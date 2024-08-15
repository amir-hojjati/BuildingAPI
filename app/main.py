# app/main.py
import uvicorn
from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI()

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)
