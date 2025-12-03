from typing import Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weather import City
from app.core.logger import logger, db_crud_handler


@db_crud_handler
async def create_city(
    session: AsyncSession,
    name: str,
    country: str,
    lat: float,
    lon: float,
    timezone: int
) -> City:
    city = City(name=name, country=country, lat=lat, lon=lon, timezone=timezone)
    session.add(city)
    await session.commit()
    await session.refresh(city)
    logger.info(f"Created city '{city.name}' (id={city.id})")
    return city


@db_crud_handler
async def get_city(session: AsyncSession, city_id: int) -> Optional[City]:
    city = await session.get(City, city_id)
    if city:
        logger.info(f"Fetched city id={city_id}: {city.name}")
    else:
        logger.warning(f"City id={city_id} not found")
    return city


@db_crud_handler
async def get_all_cities(session: AsyncSession, skip: int = 0, limit: int = 100) -> list[City]:
    result = await session.execute(select(City).offset(skip).limit(limit))
    cities = result.scalars().all()
    logger.info(f"Fetched {len(cities)} cities (skip={skip}, limit={limit})")
    return cities


@db_crud_handler
async def update_city(session: AsyncSession, city_id: int, **kwargs) -> Optional[City]:
    result = await session.execute(
        update(City)
        .where(City.id == city_id)
        .values(**kwargs)
        .returning(City)
    )
    updated = result.fetchone()
    if updated:
        await session.commit()
        logger.info(f"Updated city id={city_id} with values {kwargs}")
        return updated[0]
    logger.warning(f"Tried to update city id={city_id} but it was not found")
    return None


@db_crud_handler
async def delete_city(session: AsyncSession, city_id: int) -> bool:
    result = await session.execute(delete(City).where(City.id == city_id))
    await session.commit()
    if result.rowcount:
        logger.info(f"Deleted city id={city_id}")
        return True
    logger.warning(f"City id={city_id} not found to delete")
    return False