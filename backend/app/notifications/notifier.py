import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models.tracked_product import TrackedProduct
from .models.notification_settings import NotificationSettings
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
    # Carrega as configurações do usuário
    settings = (
        await db.execute(
            select(NotificationSettings).where(NotificationSettings.user_id == product.user_id)
        )
    ).scalar_one_or_none()
    if not settings:
        return

    message = None

    # Lógica simplificada: preço caiu
    if new_price is not None and old_price is not None:
        if new_price < old_price and settings.notify_on_drop:
            message = f"📉 Preço baixou!\n{product.product_name}\nDe R${old_price:.2f}\npara R${new_price:.2f}\n{product.url}"
        elif new_price > old_price and settings.notify_on_rise:
            message = f"📈 Preço subiu!\n{product.product_name}\nDe R${old_price:.2f}\npara R${new_price:.2f}\n{product.url}"

    # Produto voltou ao estoque
    if old_availability is False and new_availability is True and settings.notify_on_restock:
        message = f"✅ Produto voltou ao estoque!\n{product.product_name}\n{product.url}"

    # Se houver mensagem, dispara notificações em paralelo
    if message:
        if settings.email_enabled and product.user.email:
            asyncio.create_task(
                send_email_notification(product.user.email, "Alerta de Preço", message)
            )
        if settings.telegram_chat_id:
            asyncio.create_task(
                send_telegram_notification(settings.telegram_chat_id, message)
            )
