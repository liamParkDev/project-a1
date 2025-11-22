from pydantic import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "hj-db"
    MYSQL_PASSWORD: str = "Hani6967!"
    MYSQL_HOST: str = "192.168.105.81"
    MYSQL_DB: str = "projecta1"

    JWT_SECRET: str = "supersecret"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
