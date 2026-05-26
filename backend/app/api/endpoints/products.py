from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ...core.database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...models.tracked_product import TrackedProduct
from ...schemas.tracked_product import ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = TrackedProduct(
        user_id=current_user.id,
        url=product_in.url,
        store=product_in.store,
        target_price=product_in.target_price
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.get("/", response_model=List[ProductOut])
async def list_my_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(TrackedProduct).where(TrackedProduct.user_id == current_user.id)
    )
    products = result.scalars().all()
    return products

@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = await db.get(TrackedProduct, product_id)
    if not product or product.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = await db.get(TrackedProduct, product_id)
    if not product or product.user_id != current_user.id:
        raise HTTPException(status_code=404)
    await db.delete(product)
    await db.commit()
    return