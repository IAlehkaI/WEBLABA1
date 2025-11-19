from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
from .base import Base
from datetime import datetime


class NewsDB(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)