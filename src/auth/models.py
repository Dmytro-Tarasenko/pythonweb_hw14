from pydantic import BaseModel, EmailStr, Field


class UserModel(BaseModel):
    email: EmailStr
    password: str = Field(max_length=255)


class UserDB(UserModel):
    id: int
