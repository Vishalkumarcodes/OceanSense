from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Issue(Base):
    __tablename__ = 'issues'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    lat = Column(Float)
    lon = Column(Float)
    severity = Column(String(20))
    photo_path = Column(String(300), nullable=True)
    reported_by = Column(Integer, nullable=True)
    status = Column(String(30), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
