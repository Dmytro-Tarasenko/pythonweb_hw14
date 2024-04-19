from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserModel(BaseModel):
    email: EmailStr
    password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None)


class UserDB(UserModel):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
