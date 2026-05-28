import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.tracked_product import TrackedProduct
from ..models.notification_settings import NotificationSettings
from .email_sender import send_email_notification
from .telegram_sender import send_telegram_notification

logger = logging.getLogger(__name__)

async def notify_price_change(
    db: AsyncSession,
    product: TrackedProduct,
    old_price: float | None,
    new_price: float | None,
    old_availability: bool | None,
    new_availability: bool | None,
):
    result = await db.execute(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == product.user_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        return

    # Carrega user explicitamente para evitar lazy load em contexto async
    from ..models.user import User
    user = await db.get(User, product.user_id)
    if not user:
        return

    message = None

    if new_price is not None and old_price is not None:
        if new_price < old_price and settings.notify_on_drop:
            message = (
                f"📉 Preço baixou!\n{product.product_name}\n"
                f"De R${old_price:.2f} para R${new_price:.2f}\n{product.url}"
            )
        elif new_price > old_price and settings.notify_on_rise:
            message = (
                f"📈 Preço subiu!\n{product.product_name}\n"
                f"De R${old_price:.2f} para R${new_price:.2f}\n{product.url}"
            )

    if old_availability is False and new_availability is True and settings.notify_on_restock:
        message = f"✅ Produto voltou ao estoque!\n{product.product_name}\n{product.url}"

    if not message:
        return

    tasks = []
    if settings.email_enabled and user.email:
        tasks.append(send_email_notification(user.email, "Alerta de Preço", message))
    if settings.telegram_chat_id:
        tasks.append(send_telegram_notification(settings.telegram_chat_id, message))

    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Erro ao enviar notificação: {r}")