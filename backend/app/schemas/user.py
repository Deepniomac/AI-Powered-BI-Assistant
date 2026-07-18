from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """
    Base user properties shared across creation and response schemas.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: str = Field("analyst", description="Role of the user (e.g., admin, analyst, executive)")

class UserCreate(UserBase):
    """
    Schema for register request payload.
    """
    password: str = Field(..., min_length=6, description="Plaintext password to be hashed")

class UserResponse(BaseModel):
    """
    Schema representing user profile details returned by API.
    """
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    """
    Schema for login request payload.
    """
    username: str = Field(..., description="Username of the user attempting to log in")
    password: str = Field(..., description="Plaintext password to verify")

class TokenResponse(BaseModel):
    """
    Schema representing a successful login token payload.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Internal schema representing parsed information from JWT payloads.
    """
    username: Optional[str] = None
    email: Optional[str] = None
