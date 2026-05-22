from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import (
    Category as CategoryModel
)
from app.models.products import (
    Product as ProductModel,
)
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db
from app.services.products import select_products, select_product_by_id
from app.services.categories import check_category


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.post(
    "/",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db)
):
    await check_category(db, category_id=product.category_id, status_code=400)

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    await db.commit()

    return db_product


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    products = await select_products(db)
    return products


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    await check_category(db, category_id=category_id, status_code=404)
    products = await select_products(db, category_id=category_id)

    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    # product_stmt = select(ProductModel).where(
    #     ProductModel.id == product_id,
    #     ProductModel.is_active
    # )
    # product = (await db.scalars(product_stmt)).first()
    product = await select_product_by_id(db, product_id)

    # if product is None or not isinstance(product, ProductModel):
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Product not found or inactive"
    #     )

    # category_stmt = select(CategoryModel).where(
    #     CategoryModel.id == product.category_id,
    #     CategoryModel.is_active
    # )
    # category = (await db.scalars(category_stmt)).first()

    # if category is None:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Category not found or inactive"
    #     )
    # await check_category(
    #   db, category_id=product.category_id, status_code=400
    # )
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db)
):
    # product_stmt = select(ProductModel).where(
    #     ProductModel.id == product_id,
    #     ProductModel.is_active
    # )
    # product_db = (await db.scalars(product_stmt)).first()

    # if product_db is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Product not found or inactive"
    #     )

    # category_stmt = select(CategoryModel).where(
    #     CategoryModel.id == product.category_id,
    #     CategoryModel.is_active
    # )
    # category = (await db.scalars(category_stmt)).first()

    # if category is None:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Category not found or inactive"
    #     )
    product_db = await select_product_by_id(db, product_id)

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(product_db)
    return product_db


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db)
) -> dict:
    # stmt = select(ProductModel).where(
    #     ProductModel.id == product_id,
    #     ProductModel.is_active
    # )
    # product = (await db.scalars(stmt)).first()
    # if product is None:
    #     raise HTTPException(status_code=404, detail="Product not found")
    product = await select_product_by_id(db, product_id)
    if product is not None:
        product.is_active = False
    await db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
