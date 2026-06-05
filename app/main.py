from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import validate_settings
from app.routers import categories, products, users, reviews, cart


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_settings()
    yield


# Создаём приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0",
    lifespan=lifespan,
)

# Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)


# Корневой эндпоинт для проверки
@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API интернет-магазина!"}
