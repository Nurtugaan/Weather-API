import asyncio
import pytest
import tempfile
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.core.database import Base
from app.core import database as core_database
from app.services import weather_fetcher

# временный файл для sqlite
tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{tmp_db.name}"

# event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# async engine
@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        future=True,
    )
    # создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# session fixture
@pytest.fixture()
async def db_session(engine):
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with SessionLocal() as session:
        yield session

# patch core_database.AsyncSessionLocal
@pytest.fixture(autouse=True)
def patch_core_session_factory(engine, monkeypatch):
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    monkeypatch.setattr(core_database, "AsyncSessionLocal", SessionLocal)
    yield

# http client mock
class DummyResponse:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self.data

class DummyAsyncClient:
    def __init__(self, payload):
        self.payload = payload
        self.closed = False

    async def get(self, url):
        return DummyResponse(self.payload)

    async def aclose(self):
        self.closed = True

@pytest.fixture()
def mock_http_client(monkeypatch):
    default_payload = {
        "dt": 1234567890,
        "main": {"temp": 10.5, "feels_like": 8.3, "temp_min": 9.0, "temp_max": 11.0, "pressure": 1012, "humidity": 80},
        "wind": {"speed": 3.5, "deg": 200},
        "clouds": {"all": 40},
        "rain": {"1h": 0.0},
        "weather": [{"main": "Clouds", "description": "broken clouds", "icon": "04d"}],
    }

    def apply(payload=None):
        payload_to_use = payload or default_payload
        client = DummyAsyncClient(payload_to_use)

        async def _get_client():
            return client

        monkeypatch.setattr(weather_fetcher, "get_http_client", _get_client)
        return client

    return apply