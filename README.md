# Weather API

Асинхронное FastAPI-приложение для хранения городов и актуальной погоды через OpenWeatherMap.

---

## Быстрый запуск (Docker)

1. **Склонируйте проект:**
```bash
git clone https://github.com/your-username/weather-api.git
cd weather-api
````

2. **Создайте и отредактируйте `.env`:**

```bash
cp .env.example .env
```

**Пример содержимого `.env`:**

```env
DATABASE_URL=postgresql+asyncpg://weather_user:weather_pass@db:5432/weather_db
WEATHER_API_KEY=ваш_ключ_от_openweathermap
WEATHER_UPDATE_INTERVAL=600                  # сек между обновлениями (по умолчанию 10 минут)
```

3. **Запустите всё одной командой:**

```bash
docker-compose up --build
```

> Автоматически:
>
> * Запустится PostgreSQL
> * Применятся миграции Alembic
> * Запустится FastAPI на порту 8000
> * Начнётся фоновое обновление погоды

4. **Запуск теста:**

```bash
docker-compose exec -e PYTHONPATH=/app web pytest -q
```

5. **Доступ к API:**

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

6. **Остановка проекта:**

```bash
docker-compose down
```

7. **Полная очистка (включая данные БД):**

```bash
docker-compose down -v
```

---

## Полезные ссылки

* Ключ OpenWeatherMap: [https://openweathermap.org/api](https://openweathermap.org/api)