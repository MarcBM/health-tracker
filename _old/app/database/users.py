from sqlalchemy import Column, Integer, String, Boolean
from .base import Base


class User(Base):
    """Simple user model for authentication"""
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Simple permission system
    can_edit = Column(Boolean, default=False)  # True for edit permissions, False for view-only
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', can_edit={self.can_edit})>" 