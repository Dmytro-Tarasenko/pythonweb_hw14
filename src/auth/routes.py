from typing import Annotated, Any

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request

from auth.models import UserDB, UserRequest, TokenResponse
from auth.orms import User
from auth.service import Authentication
from db import get_db
from email_service.routes import send_confirmation, EmailModel

router = APIRouter(prefix="/auth",
                   tags=["Authentication"])

auth_service = Authentication()


@router.post("/register",
             response_model=UserDB,
             responses={409: {"description": "User already exists"},
                        201: {"model": UserDB}},
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def new_user(
        user: UserRequest,
        db: Annotated[Session, Depends(get_db)],
        bg_task: BackgroundTasks
) -> Any:
    exists = db.query(User).filter(User.email == user.email).first()
    if exists:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "details": [
                    {"msg":
                     f"User with email: {user.email} already registered"
                     }
                ]}
        )

    hashed_pwd = auth_service.hash_password(user.password)
    user = User(email=user.email,
                hashed_pwd=hashed_pwd)
    db.add(user)
    db.commit()

    email_param = EmailModel(email=user.email)
    res = await send_confirmation(email=email_param,
                                  bg_task=bg_task,
                                  db=db)

    ret_user = db.query(User).filter(User.email == user.email).first()

    return JSONResponse(
        status_code=201,
        content={**UserDB.from_orm(ret_user).model_dump(exclude="id"),
                 'confirmation': res['message']}
    )


@router.post("/login",
             response_model=TokenResponse,
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def login(
        user: UserRequest,
        db: Annotated[Session, Depends(get_db)]
) -> Any:
    user_db: User = db.query(User).filter(User.email == user.email).first()
    if not user_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "details": [
                    {"msg": f"User with email: {user.email} not found"}
                ]}
        )

    if not auth_service.verify_password(user.password, user_db.hashed_pwd):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "details": [
                    {"msg": "Invalid credentials"}
                ]}
        )

    if not user_db.email_confirmed:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'details': [
                    {"msg": "Email not confirmed."}
                ]
            }
        )

    access_token = auth_service.create_access_token(user.email)
    refresh_token = auth_service.create_refresh_token(user.email)
    user_db.loggedin = True
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"access_token": access_token,
                 "refresh_token": refresh_token,
                 "token_type": "bearer"}
    )


@router.post("/refresh",
             response_model=TokenResponse,
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def refresh(
        request: Request,
        user: Annotated[User, Depends(auth_service.get_refresh_user)]
) -> Any:
    if not user.loggedin:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"details": "User not logged in. Use /auth/login"}
        )
    if user.email is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"details": "Invalid credentials"}
        )
    access_token = auth_service.create_access_token(user.email)
    refresh_token = request.headers.get("Authorization").split(" ")[1]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"access_token": access_token,
                 "refresh_token": refresh_token,
                 "token_type": "bearer"}
    )


@router.post("/logout",
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def logout(
        user: Annotated[User, Depends(auth_service.get_access_user)],
        db: Annotated[Session, Depends(get_db)]
) -> Any:
    user.loggedin = False
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"details": "User logged out"}
    )
