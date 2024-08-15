# app/core/config.py
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Database connection setup
DATABASE_URL = environ.get("conn_str", 'sqlite:///:memory:')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        if 'sqlite' in DATABASE_URL:
            Base.metadata.create_all(bind=engine)
        yield db
    finally:
        db.close()
