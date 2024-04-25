from pathlib import Path
from typing import Any, Annotated
from datetime import timedelta

from fastapi import BackgroundTasks, Depends
from fastapi.routing import APIRouter
from fastapi_limiter.depends import RateLimiter
from pydantic import EmailStr, BaseModel
from fastapi_mail import (ConnectionConfig,
                          MessageSchema,
                          MessageType,
                          FastMail)
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from auth.orms import User
from settings import settings
from auth.service import Authentication
from db import get_db

auth_service = Authentication()

router = APIRouter(prefix="/email",
                   tags=["email calls"])


class EmailModel(BaseModel):
    email: EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_user,
    MAIL_PASSWORD=settings.mail_pass,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="hw13 app",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


@router.post('/send-confirmation',
             dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def send_confirmation(
        bg_task: BackgroundTasks,
        email: EmailModel,
        db: Annotated[Session, Depends(get_db)]
) -> Any:
    user_db: User = db.query(User).filter(User.email == email.email).first()
    if not user_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "details": f"User with email {email.email} not found"
            }
        )

    token = auth_service.create_access_token(email=email.email,
                                             time_to_live=timedelta(hours=24))
    token_url = router.url_path_for('confirm_email',
                                    token=token)
    message = MessageSchema(
        subject="Email confirmation",
        recipients=[email.email],
        template_body={"token_url": token_url},
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    bg_task.add_task(fm.send_message,
                     message,
                     template_name="confirmation.html")

    return {"message": f"email has been sent to {email.email}"}


@router.get('/confirm/{token:str}',
            dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def confirm_email(
        db: Annotated[Session, Depends(get_db)],
        token: str
) -> Any:
    user: User = auth_service.get_access_user(token=token,
                                              db=db)
    if user.email_confirmed:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "details": f"The email {user.email} is already confirmed."
            }
        )

    user.email_confirmed = True
    db.commit()
    return JSONResponse(
        status_code=200,
        content={
            "details": f"The email {user.email} has been confirmed."
        }
    )
