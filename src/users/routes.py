from typing import Annotated, Any

from fastapi import APIRouter, Depends, UploadFile
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import cloudinary
from cloudinary.uploader import upload, destroy
from cloudinary.utils import cloudinary_url
from starlette import status
from starlette.responses import JSONResponse, Response

from db import get_db
from users.orms import User
from users.models import UserDB
from auth.service import Authentication
from settings import settings


auth_service = Authentication()

router = APIRouter(prefix="/users",
                   tags=["users", "profile"])


@router.get("/profile/",
            dependencies=[Depends(RateLimiter(times=2, seconds=40))],
            response_model=UserDB)
async def get_profile(
        user: Annotated[User, Depends(auth_service.get_access_user)]
) -> Any:
    return UserDB.from_orm(user)


@router.post('/update-avatar/',
             dependencies=[Depends(RateLimiter(times=2, seconds=40))])
@router.patch('/update-avatar/',
              dependencies=[Depends(RateLimiter(times=2, seconds=40))])
async def update_avatar(
        user: Annotated[User, Depends(auth_service.get_access_user)],
        db: Annotated[Session, Depends(get_db)],
        avatar: UploadFile
) -> Any:
    cldry_config = cloudinary.config(secure=True)
    cldry_config._load_from_url(settings.cloudinary_url)
    cldry_response = upload(file=avatar.file,
                            public_id=f"hw13/{user.email}",
                            overwrite=True,
                            )
    avatar_url, options = cloudinary_url(
        cldry_response['public_id'],
        format=cldry_response['format'],
        width=250,
        height=250,
        crop='fill',
        gravity='face',
        version=cldry_response.get('version')
    )
    user.avatar_url = avatar_url
    db.commit()

    return JSONResponse(
        status_code=201,
        content={
            "details": f"{avatar_url}"
        }
    )


@router.delete("/avatar",
               dependencies=[Depends(RateLimiter(times=1, minutes=2))],
               responses={204: {"model": None}})
async def delete_avatar(
        user: Annotated[User, Depends(auth_service.get_access_user)],
        db: Annotated[Session, Depends(get_db)]
) -> Any:
    cldry_config = cloudinary.config(secure=True)
    cldry_config._load_from_url(settings.cloudinary_url)
    cldry_response = destroy(public_id=f"hw13/{user.email}")
    print(cldry_response)
    user.avatar_url = None
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
