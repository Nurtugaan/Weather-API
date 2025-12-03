import pytest
from sqlalchemy import text
from app.crud import city as city_crud
from app.schemas.weather import WeatherCreate
from app.services.weather_fetcher import upsert_weather as svc_upsert
from app.crud import weather as weather_crud  # для остальных CRUD операций

@pytest.mark.asyncio
async def test_create_get_update_delete_weather(db_session):
    # создаём город
    city = await city_crud.create_city(
        session=db_session, name="WeatherCity", country="WC", lat=1.0, lon=2.0, timezone=0
    )

    # create weather
    created = await weather_crud.create_weather(
        session=db_session,
        city_id=city.id,
        temp=5.5,
        feels_like=4.0,
        pressure=1000,
        humidity=50,
    )
    assert created.id is not None
    assert created.city_id == city.id

    wid = created.id

    # get
    got = await weather_crud.get_weather(session=db_session, weather_id=wid)
    assert got is not None
    assert got.temp == 5.5

    # update
    updated = await weather_crud.update_weather(session=db_session, weather_id=wid, temp=6.0)
    assert updated.temp == 6.0

    # get by city
    list_for_city = await weather_crud.get_weather_by_city(session=db_session, city_id=city.id)
    assert any(w.id == wid for w in list_for_city)

    # get_all
    all_weather = await weather_crud.get_all_weather(session=db_session)
    assert len(all_weather) >= 1

    # delete
    deleted = await weather_crud.delete_weather(session=db_session, weather_id=wid)
    assert deleted is True

    # ensure gone
    got_after = await weather_crud.get_weather(session=db_session, weather_id=wid)
    assert got_after is None

@pytest.mark.asyncio
async def test_upsert_weather_creates_and_updates(db_session):
    # создаём город
    city = await city_crud.create_city(session=db_session, name="UpsertCity", country="UC", lat=0, lon=0, timezone=0)

    wcreate = WeatherCreate(
        city_id=city.id, temp=10.0, feels_like=9.0, pressure=1015, humidity=30, timestamp=1111
    )

    # upsert (создаст)
    await svc_upsert(session=db_session, weather=wcreate)

    result = await db_session.execute(
        text("SELECT id, city_id, temp FROM weather_data WHERE city_id = :cid"),
        {"cid": city.id}
    )
    rows = result.fetchall()
    assert len(rows) == 1

    # обновляем теми же значениями — запись не создаётся заново
    wcreate2 = WeatherCreate(city_id=city.id, temp=10.0, feels_like=9.0, pressure=1015, humidity=30, timestamp=1111)
    await svc_upsert(session=db_session, weather=wcreate2)

    result2 = await db_session.execute(
        text("SELECT COUNT(*) FROM weather_data WHERE city_id = :cid"),
        {"cid": city.id}
    )
    assert result2.scalar_one() == 1

    # обновляем значение — должно обновиться
    wcreate3 = WeatherCreate(city_id=city.id, temp=11.5, feels_like=10.0, pressure=1010, humidity=35, timestamp=2222)
    await svc_upsert(session=db_session, weather=wcreate3)

    result3 = await db_session.execute(
        text("SELECT temp FROM weather_data WHERE city_id = :cid"),
        {"cid": city.id}
    )
    assert float(result3.scalar_one()) == 11.5