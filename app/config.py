import os
from pathlib import Path

from dotenv import load_dotenv

# .env в корне проекта (рядом с alembic.ini)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not str(value).strip():
        raise RuntimeError(
            f"{name} is not set or empty. "
            f"Add it to {_ENV_PATH}."
        )
    return value.strip()


def validate_settings() -> None:
    """Проверяет обязательные переменные окружения при старте приложения."""
    _require_env("SECRET_KEY")
    _require_env("DATABASE_URL")


validate_settings()

SECRET_KEY = _require_env("SECRET_KEY")
DATABASE_URL = _require_env("DATABASE_URL")
ALGORITHM = "HS256"
