from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from typing import Sequence


def get_products(
    db: Session,
    product_id: int | None = None,
    category_id: int | None = None
) -> Sequence[ProductModel] | ProductModel | None:
    if product_id is not None:
        stmt = select(ProductModel).join(CategoryModel).where(
            ProductModel.id == product_id,
            ProductModel.is_active,
            CategoryModel.is_active,
            ProductModel.stock > 0
        ).order_by(ProductModel.name)

        return db.scalars(stmt).first()

    stmt = select(ProductModel).join(CategoryModel).where(
        ProductModel.is_active,
        CategoryModel.is_active,
        ProductModel.stock > 0
    ).order_by(ProductModel.name)

    if category_id is not None:
        stmt = stmt.where(ProductModel.category_id == category_id)

    return db.scalars(stmt).all()
