from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    role: Literal["employee", "admin"] = Field(default="employee")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    login: str | None = None
    role: str | None = None
