from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import ReviewModel
from app.models.users import User as UserModel
from app.schemas import ReviewCreate, ReviewRead
from app.db_depends import get_async_db
from app.services.products import select_product_by_id, update_product_rating
from app.auth import get_current_buyer
# from app.routers.products import router as product_router


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

product_router = APIRouter(
    prefix="/products",
    tags=["reviews"],
)


@router.get('/', response_model=list[ReviewRead])
async def read_all_reviews(
    db: AsyncSession = Depends(get_async_db)
):
    """Возвращает список всех активных отзывов."""

    stmt = select(ReviewModel).where(ReviewModel.is_active)
    reviews = (await db.scalars(stmt)).all()
    return reviews


@product_router.get(
    '/{product_id}/reviews',
    response_model=list[ReviewRead]
)
async def read_review(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Возвращает список всех активных отзывов для конкретного товара."""

    await select_product_by_id(db, product_id)

    stmt = select(ReviewModel).where(
        ReviewModel.product_id == product_id,
        ReviewModel.is_active
    )
    reviews = (await db.scalars(stmt)).all()
    return reviews


@router.post('/', response_model=ReviewRead)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    user: UserModel = Depends(get_current_buyer)
):
    """Создаёт новый отзыв для конкретного товара."""

    await select_product_by_id(db, review.product_id)

    new_review = ReviewModel(**review.model_dump(), user_id=user.id)

    db.add(new_review)
    await db.commit()
    await update_product_rating(db, review.product_id)
    await db.refresh(new_review)
    return new_review


@router.delete('/{review_id}', response_model=dict)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: UserModel = Depends(get_current_buyer)
):
    """Удаляет отзыв для конкретного товара."""

    stmt = (
        select(ReviewModel).where(
            ReviewModel.id == review_id,
            ReviewModel.is_active
        )
    )
    review = (await db.scalars(stmt)).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or inactive"
        )

    if review.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    review.is_active = False
    await db.commit()
    await update_product_rating(db, review.product_id)
    return {"message": "Review has been deleted"}
