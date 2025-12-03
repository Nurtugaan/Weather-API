import pytest
from sqlalchemy import text
from app.services import weather_fetcher
from app.schemas.weather import WeatherCreate
from app.crud import city as city_crud
from app.services.weather_fetcher import weather_update_pipeline

@pytest.mark.asyncio
async def test_fetch_weather_for_city_success(db_session, mock_http_client):
    # готовим mock http клиент с дефолтной нагрузкой
    mock_http_client()

    # создаём город
    city = await city_crud.create_city(session=db_session, name="HTTPCity", country="KZ", lat=10.0, lon=20.0, timezone=6)

    # вызываем fetch (он использует get_http_client из weather_fetcher, который мы пропатчили)
    weather = await weather_fetcher.fetch_weather_for_city(city, retries=1)
    assert isinstance(weather, WeatherCreate)
    assert weather.city_id == city.id
    assert weather.temp is not None

@pytest.mark.asyncio
async def test_weather_update_pipeline_creates_entries(db_session, mock_http_client):
    # мок с payload
    mock_http_client()  # дефолтный payload

    # создаём несколько городов
    c1 = await city_crud.create_city(session=db_session, name="PipCity1", country="KZ", lat=1.0, lon=2.0, timezone=0)
    c2 = await city_crud.create_city(session=db_session, name="PipCity2", country="KZ", lat=2.0, lon=3.0, timezone=0)

    # запускаем pipeline
    await weather_update_pipeline(session=db_session, allowed_countries=["KZ"], batch_size=10)

    # Проверяем записи в weather_data
    res = await db_session.execute(text("SELECT city_id FROM weather_data"))
    rows = res.fetchall()
    city_ids = {r[0] for r in rows}
    assert c1.id in city_ids
    assert c2.id in city_ids