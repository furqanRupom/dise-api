import os

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, "..", "..", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    #   APP CONFIG
    APP_NAME: str = "Dise API"
    VERSION: str = "1.0.0"

    #   TOKEN CONFIG

    ALGORITHMS: str = "HS256"
    SECRET_ACCESS_TOKEN: str = "abdlajdlsj"  # change to yours
    SECRET_REFRESH_TOKEN: str = "abcdefg"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 900
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 64800

    # DB
    DATABASE_URL: str = "postgresql://diseuser:disepassword@localhost:5432/disedb"

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str | None = None  # optional, useful with Doc

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "dise@dise.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Your App"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # OAUTH
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""


settings = Settings()
