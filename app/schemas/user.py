from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Sai Krishna"})
    email: EmailStr = Field(..., json_schema_extra={"example": "sai@example.com"})
    password: str = Field(..., min_length=8, max_length=128, json_schema_extra={"example": "StrongPassword123"})

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty or only whitespace")
        return cleaned

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, json_schema_extra={"example": "Sai Krishna"})
    email: Optional[EmailStr] = Field(None, json_schema_extra={"example": "sai.updated@example.com"})
    password: Optional[str] = Field(None, min_length=8, max_length=128, json_schema_extra={"example": "NewStrongPassword123"})

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Name cannot be empty or only whitespace")
            return cleaned
        return v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[EmailStr]) -> Optional[EmailStr]:
        if v is not None:
            return v.strip().lower()
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
