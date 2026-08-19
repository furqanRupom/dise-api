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
    SECRET_ACCESS_TOKEN: str = "2fbb5fc0e46169f672d1109f4ae5e964102f826871a0a0946255652843129047"  # change to yours
    SECRET_REFRESH_TOKEN: str = "ae08e6325e5717272df49046c82904ca40fb22f095a0a6fc65cda318954ec609146244d37b6a13fbb3be054a4bf5043ba090923b1057b782b079a4e81d64ea85"
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

    # FRONTEND URLS
    FRONTEND_HOST: str = "http://localhost:3000"

    # FILE UPLOAD
    STORAGE_BACKEND: str = "cloudinary"

    CLOUDINARY_CLOUD_NAME: str = "sjdlk"
    CLOUDINARY_API_KEY: str = "dsjaldk"
    CLOUDINARY_API_SECRET: str = "dsjaldk;js"
    CLOUDINARY_FOLDER: str = "uploads"


settings = Settings()
