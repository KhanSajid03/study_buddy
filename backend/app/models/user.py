from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # LLM Configuration (user-specific API keys)
    openai_api_key = Column(String(255), nullable=True)
    anthropic_api_key = Column(String(255), nullable=True)
    custom_llm_endpoint = Column(String(255), nullable=True)
    custom_llm_api_key = Column(String(255), nullable=True)

    # Preferences
    preferred_llm_provider = Column(String(50), default="openai")
    preferred_model = Column(String(100), default="gpt-3.5-turbo")

    # Relationships
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}')>"
