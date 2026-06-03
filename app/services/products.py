from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.models.reviews import ReviewModel
from app.services.categories import check_category


async def select_products(
    db: AsyncSession,
    category_id: int | None = None
) -> Sequence[ProductModel] | ProductModel | None:

    stmt = select(ProductModel).join(CategoryModel).where(
        ProductModel.is_active,
        CategoryModel.is_active,
        ProductModel.stock > 0
    ).order_by(ProductModel.name)

    if category_id is not None:
        stmt = stmt.where(ProductModel.category_id == category_id)

    return (await db.scalars(stmt)).all()


async def select_product_by_id(
    db: AsyncSession,
    product_id: int,
    stock: bool = True
) -> ProductModel:

    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active,
    ).order_by(ProductModel.name)

    if stock:
        stmt = stmt.where(ProductModel.stock > 0)

    product = (await db.scalars(stmt)).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )

    await check_category(db, product.category_id, 400)
    return product


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    if product:
        product.rating = avg_rating
    await db.commit()
