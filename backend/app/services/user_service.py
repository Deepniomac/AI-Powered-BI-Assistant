from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password, verify_password

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Fetches a user from the database using their unique primary key ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Fetches a user from the database using their unique username.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Fetches a user from the database using their unique email address.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Inserts a new user record into the database, verifying username and email uniqueness,
    and hashing the password using bcrypt.
    """
    # Assert username uniqueness
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already registered"
        )
        
    # Assert email uniqueness
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )

    # Transform plaintext password to bcrypt hash
    hashed_pwd = hash_password(user_data.password)
    
    # Construct SQLAlchemy User instance
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_pwd,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """
    Authenticates user against their password hash. Supports logging in with
    either username or email.
    """
    # Lookup user by username, fall back to email
    user = get_user_by_username(db, username_or_email)
    if not user:
        user = get_user_by_email(db, username_or_email)
        
    if not user:
        return None
        
    # Verify hashed password comparison
    if not verify_password(password, user.password_hash):
        return None
        
    return user
