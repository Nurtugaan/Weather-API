import json
from pathlib import Path
from sqlalchemy import select
from app.models.weather import City
from app.core.database import AsyncSessionLocal
from app.core.logger import logger

CITY_JSON_PATH = Path("app/data/city.list.json")

async def init_cities():
    with open(CITY_JSON_PATH, "r", encoding="utf-8") as f:
        cities = json.load(f)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(City.id))
        existing_ids = set(r[0] for r in result.all())

        new_cities = []
        for city in cities:
            if city["id"] not in existing_ids:
                new_cities.append(
                    City(
                        id=city["id"],
                        name=city["name"],
                        country=city.get("country"),
                        lat=city["coord"]["lat"],
                        lon=city["coord"]["lon"]
                    )
                )

        if new_cities:
            session.add_all(new_cities)
            await session.commit()
            logger.info(f"Added {len(new_cities)} new cities")
        else:
            logger.info("No new cities to add")