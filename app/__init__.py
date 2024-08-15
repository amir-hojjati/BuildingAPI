# app/__init__.py

from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI()

# Include the router for API endpoints
app.include_router(router)

