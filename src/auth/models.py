from typing import Optional

from pydantic import BaseModel, EmailStr, Field



class UserModel(BaseModel):
    email: EmailStr
    password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None)


class UserDB(UserModel):
    id: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
