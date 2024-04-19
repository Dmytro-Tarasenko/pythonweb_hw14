from datetime import datetime, timezone, timedelta
from typing import Dict, Any, TypeAlias, Literal, Annotated
from os import getenv

from dotenv import load_dotenv
import jose
from jose import jwt
from passlib import context
import fastapi
from fastapi import security, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from auth.orms import User
from db import get_db

load_dotenv()
SECRET_256 = getenv("SECRET_256")
SECRET_512 = getenv("SECRET_512")

Scope: TypeAlias = Literal['access_token', 'refresh_token']


class Authentication:
    HASH_CONTEXT = context.CryptContext(schemes=['bcrypt'])
    ACCESS_ALGORITHM = "HS256"
    REFRESH_ALGORITHM = "HS512"
    SECRET_256 = SECRET_256
    SECRET_512 = SECRET_512
    oauth2_schema = security.OAuth2PasswordBearer(tokenUrl="/auth/login")

    def verify_password(
            self,
            plain_password: str,
            hashed_password: str
    ) -> bool:
        return self.HASH_CONTEXT.verify(secret=plain_password,
                                        hash=hashed_password)

    def hash_password(
            self,
            plain_password: str
    ) -> str:
        return self.HASH_CONTEXT.hash(plain_password)

    def create_token(
            self,
            email: str,
            scope: Scope,
            time_to_live: timedelta
    ) -> str:
        current_time = datetime.now(timezone.utc)
        expiration_time = current_time + time_to_live

        key = self.SECRET_256\
            if scope == "access_token" \
            else self.SECRET_512

        algorithm = self.ACCESS_ALGORITHM \
            if scope == "access_token" \
            else self.REFRESH_ALGORITHM

        payload = {
            "sub": email,
            "exp": expiration_time,
            "scope": scope
        }

        jwt_token = jwt.encode(claims=payload,
                               key=key,
                               algorithm=algorithm)

        return jwt_token

    def create_access_token(
            self,
            email: str,
            time_to_live: timedelta = timedelta(minutes=15)
    ) -> str:
        return self.create_token(email=email,
                                 time_to_live=time_to_live,
                                 scope="access_token")

    def create_refresh_token(
            self,
            email: str,
            time_to_live: timedelta = timedelta(days=7)
    ) -> str:
        return self.create_token(email=email,
                                 scope="refresh_token",
                                 time_to_live=time_to_live)

    def get_user(
            self,
            token: Annotated[str, Depends(oauth2_schema)],
            db: Annotated[Session, Depends(get_db)],
            scope: Scope = "access_token"
    ) -> Any:

        key = self.SECRET_256 \
            if scope == "access_token" \
            else self.SECRET_512

        algorithm = self.ACCESS_ALGORITHM \
            if scope == "access_token" \
            else self.REFRESH_ALGORITHM

        try:
            payload = jwt.decode(token=token,
                                 key=key,
                                 algorithms=[algorithm])
        except jose.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}"
            )

        if payload.get("scope") not in ["access_token", "refresh_token"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token scope"
            )

        if all([payload.get("scope") == "access_token",
                datetime.fromtimestamp(int(payload.get("exp")))
                <= datetime.now(timezone.utc)]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired. Use /auth/refresh with refresh token"
            )

        if all([payload.get("scope") == "refresh_token",
                datetime.fromtimestamp(int(payload.get("exp")))
                <= datetime.now(timezone.utc)]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired. Use /auth/login to get new tokens"
            )

        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token scope"
            )

        user = db.query(User).filter(
            User.email == email
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        return user
