from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import weather as weather_crud
from app.core.database import get_session
from app.schemas.weather import WeatherCreate, WeatherRead

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.post("/", response_model=WeatherRead)
async def create_weather(weather: WeatherCreate, session: AsyncSession = Depends(get_session)):
    created_weather = await weather_crud.create_weather(session, **weather.model_dump())
    return WeatherRead.model_validate(created_weather)

@router.get("/{weather_id}", response_model=WeatherRead)
async def get_weather(weather_id: int, session: AsyncSession = Depends(get_session)):
    weather_obj = await weather_crud.get_weather(session, weather_id)
    if not weather_obj:
        raise HTTPException(status_code=404, detail="Weather entry not found")
    return WeatherRead.model_validate(weather_obj)

@router.get("/city/{city_id}", response_model=List[WeatherRead])
async def get_weather_by_city(city_id: int, session: AsyncSession = Depends(get_session)):
    weather_list = await weather_crud.get_weather_by_city(session, city_id)
    return [WeatherRead.model_validate(w) for w in weather_list]

@router.put("/{weather_id}", response_model=WeatherRead)
async def update_weather(weather_id: int, weather: WeatherCreate, session: AsyncSession = Depends(get_session)):
    updated_weather = await weather_crud.update_weather(session, weather_id, **weather.model_dump())
    if not updated_weather:
        raise HTTPException(status_code=404, detail="Weather entry not found")
    return WeatherRead.model_validate(updated_weather)

@router.delete("/{weather_id}", response_model=dict)
async def delete_weather(weather_id: int, session: AsyncSession = Depends(get_session)):
    success = await weather_crud.delete_weather(session, weather_id)
    if not success:
        raise HTTPException(status_code=404, detail="Weather entry not found")
    return {"detail": "Weather entry deleted successfully"}

@router.get("/", response_model=List[WeatherRead])
async def get_all_weather_endpoint(session: AsyncSession = Depends(get_session)):
    weather_list = await weather_crud.get_all_weather(session)
    return [WeatherRead.model_validate(w) for w in weather_list]