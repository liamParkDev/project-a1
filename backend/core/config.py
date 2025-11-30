import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

ENV_FILE = os.path.join(BASE_DIR, "env", "dev.env")

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    JWT_ALGORITHM: str = "HS256"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    JWT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8"
    )

settings = Settings()
