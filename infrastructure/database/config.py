from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(key="DATABASE_URL", default="")
    ASYNC_DATABASE_URL : str = os.getenv(key="ASYNC_DATABASE_URL", default="")
    debug : bool = bool(os.getenv(key= "DEBUG_MODE",default=False))

settings = Settings()
