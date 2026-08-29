import re
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """
    User Registration Pydantic Schema.

    Validates payload parameters required during user registration, enforcing
    strict password complexity guidelines.

    Args/Attributes:
        full_name (str): Full legal or display name of user (3-150 chars).
        username (str): Unique handle containing letters, numbers, and underscores.
        phone_number (str): Valid contact phone number.
        email (EmailStr): Valid unique email address.
        password (str): Password string (min 10 chars, uppercase, lowercase, digit, special char).
    """

    full_name: str = Field(..., min_length=2, max_length=150, description="Full display name of user")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$", description="Unique username handle")
    phone_number: str = Field(..., min_length=10, max_length=20, description="Contact phone number")
    email: EmailStr = Field(..., description="Valid unique email address")
    password: str = Field(..., min_length=10, max_length=128, description="Secure password requiring high complexity")

    @field_validator("password")
    @classmethod
    def validate_secure_password(cls, password: str) -> str:
        """Enforces strong password rules for maximum security."""
        if len(password) < 10:
            raise ValueError("Password must be at least 10 characters long.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter (A-Z).")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter (a-z).")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit (0-9).")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            raise ValueError("Password must contain at least one special character (e.g. @$!%*?&#).")
        return password


class UserLogin(BaseModel):
    """
    User Authentication Pydantic Schema.

    Args/Attributes:
        identifier (str): Flexible credential (Email, Username, or Phone number).
        password (str): User plain text password for verification.
    """

    identifier: str = Field(..., description="Email, Username, or Phone Number")
    password: str = Field(..., description="User password string")


class UserResponse(BaseModel):
    """
    User Profile Response Pydantic Schema.

    Exposes public user profile details without exposing password hashes.

    Args/Attributes:
        id (UUID): User unique ID.
        full_name (str): User full name.
        username (str): User username handle.
        phone_number (str): User contact phone.
        email (EmailStr): User email address.
        account_status (str): Current status ('ACTIVE', 'SUSPENDED', 'BLOCKED').
        created_at (datetime): UTC registration timestamp.
    """

    id: UUID
    full_name: str
    username: str
    phone_number: str
    email: EmailStr
    account_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    """
    User Search Item Response Pydantic Schema.

    Used when searching for users to send money or request payments.

    Args/Attributes:
        id (UUID): User UUID.
        full_name (str): User display name.
        username (str): User handle.
        phone_number (str): Phone number.
        email (EmailStr): Email address.
    """

    id: UUID
    full_name: str
    username: str
    phone_number: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Authentication Token Response Pydantic Schema.

    Args/Attributes:
        access_token (str): Signed JWT access token string.
        token_type (str): Token type scheme (Default: 'bearer').
        user (UserResponse): Profile details of authenticated user.
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        from_attributes = True
