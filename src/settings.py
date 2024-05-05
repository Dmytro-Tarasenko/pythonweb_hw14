import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

dot_env_path = Path(__file__).parent / 'dev.env'
# dot_env_path = Path(__file__).parent / '.env'


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=dot_env_path,
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    sqlalchemy_url: str
    secret_256: str
    secret_512: str
    access_algorithm: str
    refresh_algorithm: str
    mail_user: str
    mail_pass: str
    mail_server: str
    mail_port: int
    mail_from: str
    redis_server: str
    redis_port: int
    redis_pass: str
    cloudinary_url: str


# production environment
settings = EnvSettings()
print(settings)
# development environmetn
# settings = EnvSettings(_env_file='dev.env')
