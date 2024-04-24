from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8',
                                      extra='allow')


class AppSettings(BaseModel):
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
    cloudinary_url: str


__env_settings = EnvSettings()
settings = AppSettings(**__env_settings.model_dump(warnings=False))
print(settings)
