from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import (
    Category as CategoryModel
)
from app.models.products import (
    Product as ProductModel,
)
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_db
from app.services.products import get_products
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
    db: Session = Depends(get_db)
):
    # category_stmt = select(CategoryModel).where(
    #     CategoryModel.id == product.category_id,
    #     CategoryModel.is_active
    # )
    # category = db.scalars(category_stmt).first()

    # if category is None:
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Category not found or inactive"
    #     )
    check_category(db, product=product, status_code=400)

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("/", response_model=list[ProductSchema])
async def get_all_products(db: Session = Depends(get_db)):
    # stmt = select(ProductModel).join(CategoryModel).where(
    #     ProductModel.is_active,
    #     CategoryModel.is_active,
    #     ProductModel.stock > 0
    # )
    # products = db.scalars(stmt).all()
    products = get_products(db)
    return products


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    # category_stmt = select(CategoryModel).where(
    #     CategoryModel.id == category_id,
    #     CategoryModel.is_active
    # )
    # category = db.scalars(category_stmt).first()

    # if category is None:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Category not found or inactive"
    #     )
    check_category(db, category_id=category_id, status_code=404)

    # products_stmt = select(ProductModel).where(
    #     ProductModel.category_id == category_id,
    #     ProductModel.is_active
    # )
    # products = db.scalars(products_stmt).all()
    products = get_products(db, category_id=category_id)

    return products


@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):

    product_stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active
    )
    product = db.scalars(product_stmt).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )

    category_stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id,
        CategoryModel.is_active
    )
    category = db.scalars(category_stmt).first()

    if category is None:
        raise HTTPException(
            status_code=400,
            detail="Category not found or inactive"
        )

    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    product_stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active
    )
    product_db = db.scalars(product_stmt).first()

    if product_db is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found or inactive"
        )

    category_stmt = select(CategoryModel).where(
        CategoryModel.id == product.category_id,
        CategoryModel.is_active
    )
    category = db.scalars(category_stmt).first()

    if category is None:
        raise HTTPException(
            status_code=400,
            detail="Category not found or inactive"
        )

    db.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump())
    )
    db.commit()
    db.refresh(product_db)
    return product_db


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> dict:
    stmt = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active
    )
    product = db.scalars(stmt).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    db.commit()

    return {"status": "success", "message": "Product marked as inactive"}
