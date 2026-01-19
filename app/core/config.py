import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    )
    SMTP_HOST:str= os.getenv("SMTP_HOST")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM:str = os.getenv("EMAIL_FROM")
    CLOUD_NAME: str = os.getenv("CLOUD_NAME")
    API_KEY: str = os.getenv("API_KEY")
    API_SECRET: str = os.getenv("API_SECRET")

settings = Settings()

if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")