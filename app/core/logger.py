import logging
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Crud Decorator
def db_crud_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session: AsyncSession | None = kwargs.get("session")
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            logger.error(f"Database operation failed in {func.__name__}: {e}")
            raise
    return wrapper