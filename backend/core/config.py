import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("APP_ENV", "local")  # local / dev / prod

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "env")

ENV_FILE_MAP = {
    "local": os.path.join(ENV_DIR, "local.env"),
    "dev": None,   # dev는 K8s secret 사용
    "live": None,  # prod도 K8s secret 사용
}

class Settings(BaseSettings):
    APP_ENV: str = ENV
    JWT_ALGORITHM: str = "HS256"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    JWT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_MAP.get(ENV),
        env_file_encoding="utf-8"
    )

settings = Settings()
