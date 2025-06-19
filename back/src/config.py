from functools import lru_cache
import os
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str
    TOKEN_ACCESS_EXPIRE_MINUTES: int
    TOKEN_REFRESH_EXPIRE_DAYS: int
    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str

    env_file: ClassVar[str] = ".env.production" if os.getenv('ENV') == 'production' else ".env.development"
    
    model_config = SettingsConfigDict(env_file=env_file)

@lru_cache
def get_settings():
    return Settings()