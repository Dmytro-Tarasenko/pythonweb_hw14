from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from starlette import status

from auth.models import UserDB, UserModel
from auth.orms import User
from auth.service import Authentication
from db import get_db

router = APIRouter(prefix="/auth",
                   tags=["Authentication"])

auth_service = Authentication()

@router.post("/register", response_model=UserDB)
async def new_user(
        user: UserModel,
        db: Annotated[Session, Depends(get_db)]
) -> Any:
    exists = db.query(User).filter(User.email == user.email).first()
    if exists:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "details": [
                    {"msg":
                     f"User with emsil: {user.email} already registered"
                     }
                ]}
        )

    hashed_pwd = auth_service.hash_password(user.password)
    user = User(email=user.email,
                hashed_pwd=hashed_pwd)
    db.add(user)
    db.commit()

    ret_user = db.query(User).filter(User.email == user.email).first()

    return UserDB.from_orm(ret_user)
