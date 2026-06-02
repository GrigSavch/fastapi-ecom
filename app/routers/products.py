from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_async_db
from app.services.products import select_products, select_product_by_id
from app.services.categories import check_category
from app.auth import get_current_seller


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
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    await check_category(db, category_id=product.category_id, status_code=400)

    db_product = ProductModel(
        **product.model_dump(),
        seller_id=current_user.id
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

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
    product = await select_product_by_id(db, product_id)
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    product_db = await select_product_by_id(db, product_id)

    if product_db.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products"
        )

    await check_category(db, category_id=product.category_id, status_code=400)

    await db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(product_db)
    return product_db


@router.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    product = await select_product_by_id(db, product_id)

    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products"
        )

    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return product
