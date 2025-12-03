from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    WEATHER_API_KEY: str
    WEATHER_UPDATE_INTERVAL: int = 600
    WEATHER_ALLOWED_COUNTRIES: List[str] = ["KZ"]

    class Config:
        env_file = ".env"

settings = Settings()
