from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks
from fastapi.routing import APIRouter
from pydantic import EmailStr, BaseModel
from fastapi_mail import (ConnectionConfig,
                          MessageSchema,
                          MessageType,
                          FastMail)

from settings import settings

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


@router.post('/send')
async def send_confirmation(
        bg_task: BackgroundTasks,
        email: EmailModel
) -> Any:
    pass


@router.get('/confirm/{token:str}')
async def confirm_email():
    pass

print(router.url_path_for('confirm_email', token='asdasdada'))
