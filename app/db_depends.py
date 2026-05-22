from app.database import async_session_maker
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и закрывает её после обработки.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------- Асинхронная сессия -------------------------


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с бд PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
