from uuid import UUID
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    id: UUID
    email: EmailStr
    role : str 
    full_name: str 
    phone_number : str 

    class Config:
        # SQLAlchemy model support
        from_attributes = True   



class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=150)
    phone_number: str
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=8)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    role: Literal["patient", "doctor"] = "patient"


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    phone_number: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True 

