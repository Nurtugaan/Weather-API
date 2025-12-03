import asyncio
from typing import List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from app.models.weather import City, WeatherData
from app.schemas.weather import WeatherCreate
from app.core.config import settings
from app.core.logger import logger

SEM = asyncio.Semaphore(10)
async_client: Optional[httpx.AsyncClient] = None

# ---------------------
# HTTP CLIENT
# ---------------------
async def get_http_client() -> httpx.AsyncClient:
    global async_client
    if async_client is None:
        async_client = httpx.AsyncClient(timeout=10)
    return async_client

async def close_http_client():
    global async_client
    if async_client:
        await async_client.aclose()
        async_client = None

# ---------------------
# FETCH WEATHER WITH RETRIES
# ---------------------
async def fetch_weather_for_city(
    city: City, retries: int = 3, backoff: float = 1.0
) -> Optional[WeatherCreate]:
    client = await get_http_client()
    url = (
        f"http://api.openweathermap.org/data/2.5/weather?"
        f"lat={city.lat}&lon={city.lon}&appid={settings.WEATHER_API_KEY}&units=metric"
    )

    for attempt in range(1, retries + 1):
        try:
            async with SEM:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()  # Можно сделать await resp.json() если используешь async httpx
            break
        except httpx.HTTPError as e:
            logger.warning(f"[{city.name}] Attempt {attempt}/{retries} failed: {e}")
            if attempt == retries:
                logger.error(f"[{city.name}] All retries failed")
                return None
            await asyncio.sleep(backoff * attempt)

    # Проверяем, что данные есть
    if not data or "main" not in data:
        logger.error(f"[{city.name}] No weather data received")
        return None

    weather_info = data.get("weather", [{}])[0]
    main_info = data.get("main", {})
    wind_info = data.get("wind", {})
    clouds_info = data.get("clouds", {})
    rain_info = data.get("rain", {})

    return WeatherCreate(
        city_id=city.id,
        temp=main_info.get("temp"),
        feels_like=main_info.get("feels_like"),
        temp_min=main_info.get("temp_min"),
        temp_max=main_info.get("temp_max"),
        pressure=main_info.get("pressure"),
        humidity=main_info.get("humidity"),
        wind_speed=wind_info.get("speed"),
        wind_deg=wind_info.get("deg"),
        clouds=clouds_info.get("all"),
        rain_1h=rain_info.get("1h"),
        weather_main=weather_info.get("main"),
        weather_description=weather_info.get("description"),
        weather_icon=weather_info.get("icon"),
        timestamp=data.get("dt"),
    )

# ---------------------
# UPSERT WEATHER
# ---------------------
async def upsert_weather(session: AsyncSession, weather: WeatherCreate):
    try:
        stmt = select(WeatherData).where(WeatherData.city_id == weather.city_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            updated = False
            for attr, value in weather.model_dump().items():
                if getattr(existing, attr) != value:
                    setattr(existing, attr, value)
                    updated = True
            if updated:
                await session.commit()
                await session.refresh(existing)
                logger.info(f"[{weather.city_id}] Weather updated")
            else:
                logger.info(f"[{weather.city_id}] No changes, skipping update")
        else:
            weather_obj = WeatherData(**weather.model_dump())
            session.add(weather_obj)
            await session.commit()
            await session.refresh(weather_obj)
            logger.info(f"[{weather.city_id}] Weather created")
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"[{weather.city_id}] DB error: {e}")

# ---------------------
# GET CITIES
# ---------------------
async def get_cities_from_db(
    session: AsyncSession, allowed_countries: Optional[List[str]] = None
) -> List[City]:
    if allowed_countries is None:
        allowed_countries = settings.WEATHER_ALLOWED_COUNTRIES
    stmt = select(City)
    if allowed_countries:
        stmt = stmt.where(City.country.in_(allowed_countries))
    result = await session.execute(stmt)
    return result.scalars().all()

# ---------------------
# WEATHER UPDATE PIPELINE (BATCH)
# ---------------------
async def weather_update_pipeline(
    session: AsyncSession, allowed_countries: Optional[List[str]] = None, batch_size: int = 20
):
    cities = await get_cities_from_db(session, allowed_countries)

    for i in range(0, len(cities), batch_size):
        batch = cities[i:i + batch_size]
        tasks = [fetch_weather_for_city(city) for city in batch]
        for coro in asyncio.as_completed(tasks):  # as_completed позволяет обрабатывать данные по мере готовности
            weather = await coro
            if weather:
                await upsert_weather(session, weather)

# ---------------------
# PERIODIC UPDATE
# ---------------------
async def start_periodic_weather_update(
    session: AsyncSession, allowed_countries: Optional[List[str]] = None
):
    try:
        while True:
            logger.info("Starting weather update...")
            try:
                await weather_update_pipeline(session, allowed_countries)
                logger.info("Weather update completed")
            except Exception as e:
                logger.error(f"Error during weather update: {e}")
            await asyncio.sleep(settings.WEATHER_UPDATE_INTERVAL)
    finally:
        await close_http_client()