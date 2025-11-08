from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    custom_llm_endpoint: Optional[str] = None
    custom_llm_api_key: Optional[str] = None
    preferred_llm_provider: Optional[str] = None
    preferred_model: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    preferred_llm_provider: str
    preferred_model: str
    has_openai_key: bool = False
    has_anthropic_key: bool = False
    has_custom_endpoint: bool = False

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
