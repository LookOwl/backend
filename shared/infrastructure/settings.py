from pydantic_settings import BaseSettings
from pydantic import field_validator
from dotenv import load_dotenv
import os
import urllib.parse as urlparse

load_dotenv(
    dotenv_path="../../.env"
)

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(key="DATABASE_URL", default="")
    ASYNC_DATABASE_URL : str = os.getenv(key="ASYNC_DATABASE_URL", default="")
    REDIS_URL : str = os.getenv(key="REDIS_URL",default="")
    HUGGINGFACE_KEY : str = os.getenv(key="HUGGINGFACE_KEY", default="")
    debug : bool = bool(os.getenv(key= "DEBUG_MODE",default=False))
    JWT_SECRET_KEY : str = str(os.getenv(key= "JWT_SECRET_KEY",default="This is large key to prevent security violations"))
    JWT_EXPIRE_TIME_IN_MINUTES : int = int(os.getenv(key= "JWT_EXPIRE_TIME_IN_MINUTES",default=30))
    JWT_ALGORITHM : str = str(os.getenv(key="JWT_ALGORITHM",default="HS256"))

    @field_validator("ASYNC_DATABASE_URL", mode="after")
    @classmethod
    def fix_ssl_mode(cls, v: str) -> str:
        if v and "asyncpg" in v:
            url_parts = list(urlparse.urlparse(v))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            
            if 'sslmode' in query:
                query['ssl'] = query.pop('sslmode')
            
            query.pop('channel_binding', None)
            query.pop('gssencmode', None)
            
            url_parts[4] = urlparse.urlencode(query)
            return urlparse.urlunparse(url_parts)
        return v

settings = Settings()
