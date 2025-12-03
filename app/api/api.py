from fastapi import FastAPI
from app.api.endpoints import city, weather

app = FastAPI(
    title="Weather API",
    version="1.0.0",
    description="API для работы с городами и погодой"
)

app.include_router(city.router)
app.include_router(weather.router)