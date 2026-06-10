from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(key="DATABASE_URL", default="")
    ASYNC_DATABASE_URL : str = os.getenv(key="ASYNC_DATABASE_URL", default="")
    REDIS_URL : str = os.getenv(key="REDIS_URL",default="")
    debug : bool = bool(os.getenv(key= "DEBUG_MODE",default=False))

    @field_validator("ASYNC_DATABASE_URL", mode="after")
    @classmethod
    def fix_ssl_mode(cls, v: str) -> str:
        if v and "asyncpg" in v and "sslmode" in v:
            return v.replace("sslmode", "ssl")
        return v

settings = Settings()
