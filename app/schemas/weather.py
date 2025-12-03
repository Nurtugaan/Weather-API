from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Schema for City data
class CityCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    country: Optional[str] = None
    lat: float
    lon: float
    timezone: Optional[int] = None

class CityRead(CityCreate):
    id: int

# Schema for Weather data
class WeatherCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_id: int
    temp: Optional[float] = None
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    pressure: Optional[int] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    wind_deg: Optional[int] = None
    clouds: Optional[int] = None
    rain_1h: Optional[float] = None
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    weather_icon: Optional[str] = None
    timestamp: Optional[int] = None

class WeatherRead(WeatherCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None