from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weather import WeatherData
from app.core.logger import logger, db_crud_handler


@db_crud_handler
async def create_weather(session: AsyncSession, city_id: int, **kwargs) -> WeatherData:
    weather = WeatherData(city_id=city_id, **kwargs)
    session.add(weather)
    await session.commit()
    await session.refresh(weather)
    logger.info(f"Created weather id={weather.id} for city_id={city_id}")
    return weather


@db_crud_handler
async def get_weather(session: AsyncSession, weather_id: int) -> Optional[WeatherData]:
    weather = await session.get(WeatherData, weather_id)
    if weather:
        logger.info(f"Fetched weather id={weather_id} for city_id={weather.city_id}")
    else:
        logger.warning(f"Weather id={weather_id} not found")
    return weather


@db_crud_handler
async def get_weather_by_city(session: AsyncSession, city_id: int) -> list[WeatherData]:
    result = await session.execute(select(WeatherData).where(WeatherData.city_id == city_id))
    weather_list = result.scalars().all()
    logger.info(f"Fetched {len(weather_list)} weather entries for city_id={city_id}")
    return weather_list


@db_crud_handler
async def update_weather(session: AsyncSession, weather_id: int, **kwargs) -> Optional[WeatherData]:
    result = await session.execute(
        update(WeatherData)
        .where(WeatherData.id == weather_id)
        .values(**kwargs)
        .returning(WeatherData)
    )
    updated = result.fetchone()
    if updated:
        await session.commit()
        logger.info(f"Updated weather id={weather_id} with values {kwargs}")
        return updated[0]
    logger.warning(f"Tried to update weather id={weather_id} but it was not found")
    return None


@db_crud_handler
async def delete_weather(session: AsyncSession, weather_id: int) -> bool:
    result = await session.execute(delete(WeatherData).where(WeatherData.id == weather_id))
    await session.commit()
    if result.rowcount:
        logger.info(f"Deleted weather id={weather_id}")
        return True
    logger.warning(f"Weather id={weather_id} not found to delete")
    return False

@db_crud_handler
async def get_all_weather(session: AsyncSession) -> list[WeatherData]:
    result = await session.execute(select(WeatherData))
    weather_list = result.scalars().all()
    logger.info(f"Fetched all weather entries, total={len(weather_list)}")
    return weather_list