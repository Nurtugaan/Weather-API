import asyncio
import uvicorn
from fastapi import FastAPI
from app.api.endpoints import city, weather
from app.services.init_cities import init_cities
from app.services import weather_fetcher
from app.core.database import get_session
from app.core.config import settings
from app.core.logger import logger
import time

app = FastAPI(title="Weather API Test", version="1.0.0")

app.include_router(city.router)
app.include_router(weather.router)


@app.on_event("startup")
async def startup_event():
    await init_cities()
    logger.info("City initialization completed.")

    async def start_weather_updater():
        while True:
            start_time = time.time()
            logger.info("Weather updater iteration started")

            try:
                async for session in get_session():
                    try:
                        await weather_fetcher.weather_update_pipeline(
                            session, settings.WEATHER_ALLOWED_COUNTRIES
                        )
                        await session.commit()
                        logger.info("Weather update completed and committed.")
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Error during weather update pipeline: {e}")
                    break
            except Exception as e:
                logger.error(f"Error obtaining database session: {e}")

            elapsed = time.time() - start_time
            sleep_time = max(settings.WEATHER_UPDATE_INTERVAL - elapsed, 0)
            logger.info(f"Weather updater iteration finished, sleeping {sleep_time:.1f}s...")
            await asyncio.sleep(sleep_time)

    asyncio.create_task(start_weather_updater())


@app.on_event("shutdown")
async def shutdown_event():
    await weather_fetcher.close_http_client()
    logger.info("HTTP client closed.")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )