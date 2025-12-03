from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(10))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timezone = Column(Integer)

    weather = relationship("WeatherData", back_populates="city")


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)

    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"))
    city = relationship("City", back_populates="weather")

    temp = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    pressure = Column(Integer)
    humidity = Column(Integer)

    wind_speed = Column(Float)
    wind_deg = Column(Integer)

    clouds = Column(Integer)
    rain_1h = Column(Float)

    weather_main = Column(String(50))
    weather_description = Column(String(255))
    weather_icon = Column(String(10))

    timestamp = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )