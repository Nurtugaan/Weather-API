# tests/test_crud_city.py
import pytest
from app.crud import city as city_crud
from app.models.weather import City

@pytest.mark.asyncio
async def test_create_get_update_delete_city(db_session):
    # create
    created = await city_crud.create_city(
        session=db_session,
        name="TestCity",
        country="TC",
        lat=12.34,
        lon=56.78,
        timezone=3,
    )
    assert isinstance(created, City)
    assert created.id is not None
    assert created.name == "TestCity"

    city_id = created.id

    # get
    got = await city_crud.get_city(session=db_session, city_id=city_id)
    assert got is not None
    assert got.name == "TestCity"

    # update
    updated = await city_crud.update_city(session=db_session, city_id=city_id, name="NewName")
    assert updated is not None
    assert updated.name == "NewName"

    # get_all (should include at least our city)
    all_cities = await city_crud.get_all_cities(session=db_session, skip=0, limit=10)
    assert any(c.id == city_id for c in all_cities)

    # delete
    deleted = await city_crud.delete_city(session=db_session, city_id=city_id)
    assert deleted is True

    # ensure gone
    got_after = await city_crud.get_city(session=db_session, city_id=city_id)
    assert got_after is None