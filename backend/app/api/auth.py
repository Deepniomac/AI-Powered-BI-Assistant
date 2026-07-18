from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.services.user_service import create_user, authenticate_user
from app.auth.security import create_access_token, get_current_user
from app.models.user import User

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Endpoint to register a new user. Checks for existing duplicates, hashes
    password, commits to database, and returns user details without credentials.
    """
    return create_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)) -> dict:
    """
    Endpoint to log in. Validates provided username or email against database,
    verifies password hash, and yields a JWT access token.
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token with sub set to unique username
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Protected endpoint to retrieve profile details of the currently authenticated
    user using their active JWT token.
    """
    return current_user
