import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.tracked_product import TrackedProduct
from ..models.user import User
from ..schemas.tracked_product import ProductCreate

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, user: User, data: ProductCreate) -> TrackedProduct:
        product = TrackedProduct(
            user_id=user.id,
            url=str(data.url),
            store=data.store,
            target_price=data.target_price,
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        logger.info(f"Produto criado: {product.id} para usuário {user.id}")
        return product

    async def get_user_products(self, user: User) -> list[TrackedProduct]:
        result = await self.db.execute(
            select(TrackedProduct).where(TrackedProduct.user_id == user.id)
        )
        return result.scalars().all()

    async def get_product_by_id(self, product_id: str, user: User) -> TrackedProduct | None:
        product = await self.db.get(TrackedProduct, product_id)
        if not product or product.user_id != user.id:
            return None
        return product

    async def delete_product(self, product_id: str, user: User) -> bool:
        product = await self.get_product_by_id(product_id, user)
        if not product:
            return False
        await self.db.delete(product)
        await self.db.commit()
        return True