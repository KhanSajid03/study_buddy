from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.utils.auth import (
    get_password_hash,
    create_access_token,
    authenticate_user,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    if user_data.email:
        existing_email = (
            db.query(User).filter(User.email == user_data.email).first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Prepare response
    response = UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at,
        preferred_llm_provider=new_user.preferred_llm_provider,
        preferred_model=new_user.preferred_model,
        has_openai_key=bool(new_user.openai_api_key),
        has_anthropic_key=bool(new_user.anthropic_api_key),
        has_custom_endpoint=bool(new_user.custom_llm_endpoint),
    )

    return response


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and receive JWT token"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
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
