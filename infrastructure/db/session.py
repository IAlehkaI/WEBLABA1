from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .base import Base
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/newsdb")

engine = create_engine(DB_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()