from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import city as city_crud
from app.core.database import get_session
from app.schemas.weather import CityCreate, CityRead

router = APIRouter(prefix="/cities", tags=["Cities"])

@router.post("/", response_model=CityRead)
async def create_city(city: CityCreate, session: AsyncSession = Depends(get_session)):
    created_city = await city_crud.create_city(session, **city.model_dump())
    return CityRead.model_validate(created_city)

@router.get("/{city_id}", response_model=CityRead)
async def get_city(city_id: int, session: AsyncSession = Depends(get_session)):
    city_obj = await city_crud.get_city(session, city_id)
    if not city_obj:
        raise HTTPException(status_code=404, detail="City not found")
    return CityRead.model_validate(city_obj)

@router.get("/", response_model=List[CityRead])
async def get_all_cities(skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)):
    cities = await city_crud.get_all_cities(session, skip=skip, limit=limit)
    return [CityRead.model_validate(c) for c in cities]

@router.put("/{city_id}", response_model=CityRead)
async def update_city(city_id: int, city: CityCreate, session: AsyncSession = Depends(get_session)):
    updated_city = await city_crud.update_city(session, city_id, **city.model_dump())
    if not updated_city:
        raise HTTPException(status_code=404, detail="City not found")
    return CityRead.model_validate(updated_city)

@router.delete("/{city_id}", response_model=dict)
async def delete_city(city_id: int, session: AsyncSession = Depends(get_session)):
    success = await city_crud.delete_city(session, city_id)
    if not success:
        raise HTTPException(status_code=404, detail="City not found")
    return {"detail": "City deleted successfully"}