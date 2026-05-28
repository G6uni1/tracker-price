from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...services.product_service import ProductService
from ...schemas.tracked_product import ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(db)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def add_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(current_user, product_in)


@router.get("/", response_model=List[ProductOut])
async def list_my_products(
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    return await service.get_user_products(current_user)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    product = await service.get_product_by_id(product_id, current_user)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service),
):
    deleted = await service.delete_product(product_id, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Produto não encontrado")