from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel


async def check_category(
    db: AsyncSession,
    category_id: int,
    status_code: int = 404
) -> CategoryModel:
    if category_id is not None:
        category_stmt = select(CategoryModel).where(
            CategoryModel.id == category_id,
            CategoryModel.is_active
        )
    category = (await db.scalars(category_stmt)).first()

    if category is None:
        raise HTTPException(
            status_code=status_code,
            detail="Category not found or inactive"
        )
    return category
