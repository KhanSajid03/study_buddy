from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's settings and API keys"""
    # Update fields if provided
    if user_update.email is not None:
        # Check if email already exists
        existing = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        current_user.email = user_update.email

    if user_update.openai_api_key is not None:
        current_user.openai_api_key = user_update.openai_api_key

    if user_update.anthropic_api_key is not None:
        current_user.anthropic_api_key = user_update.anthropic_api_key

    if user_update.custom_llm_endpoint is not None:
        current_user.custom_llm_endpoint = user_update.custom_llm_endpoint

    if user_update.custom_llm_api_key is not None:
        current_user.custom_llm_api_key = user_update.custom_llm_api_key

    if user_update.preferred_llm_provider is not None:
        if user_update.preferred_llm_provider not in ["openai", "anthropic", "custom"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid LLM provider",
            )
        current_user.preferred_llm_provider = user_update.preferred_llm_provider

    if user_update.preferred_model is not None:
        current_user.preferred_model = user_update.preferred_model

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        preferred_llm_provider=current_user.preferred_llm_provider,
        preferred_model=current_user.preferred_model,
        has_openai_key=bool(current_user.openai_api_key),
        has_anthropic_key=bool(current_user.anthropic_api_key),
        has_custom_endpoint=bool(current_user.custom_llm_endpoint),
    )
