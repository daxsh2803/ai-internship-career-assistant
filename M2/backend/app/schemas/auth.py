
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Unique user email address", examples=["student@university.edu"])
    password: str = Field(..., min_length=8, description="Plaintext password (min 8 chars)")
    full_name: str = Field(..., min_length=2, max_length=255, examples=["Alex Morgan"])
    role: str = Field(default="STUDENT", description="STUDENT, RECRUITER, or ADMIN")

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
