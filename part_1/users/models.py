from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserModel(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)


class UserRequest(UserModel):
    password: str = Field(max_length=255)


class UserDB(UserModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hashed_pwd: str = Field(max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


if __name__ == "__main__":
    some_db = UserDB(email='email@sdf.net',
                     password='password',
                     full_name='full_name',
                     id=1)
    print(some_db)
