from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.categories import (
    Category as CategoryModel
)
from app.models.products import (
    Product as ProductModel,
)
from app.schemas import ProductCreate


def check_category(
    db: Session,
    product: ProductCreate | None = None,
    category_id: int | None = None,
    status_code: int = 404
) -> CategoryModel:
    if category_id is not None:
        category_stmt = select(CategoryModel).where(
            CategoryModel.id == category_id,
            CategoryModel.is_active
        )

    if product is not None:
        category_stmt = select(CategoryModel).where(
            CategoryModel.id == product.category_id,
            CategoryModel.is_active
        )
    category = db.scalars(category_stmt).first()

    if category is None:
        raise HTTPException(
            status_code=status_code,
            detail="Category not found or inactive"
        )
    return category
