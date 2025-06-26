"""
SQLAlchemy models for Taskflow Backend API.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    """User ORM model for persistent authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    hashed_password = Column(String(256), nullable=False)
    disabled = Column(Boolean, default=False, nullable=False)

    tasks = relationship("Task", back_populates="owner")


class Category(Base):
    """Task category."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)


class Task(Base):
    """A task belonging to a user and a category."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(String(1000))
    status = Column(String(32), nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks")

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category")
