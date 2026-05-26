import os
import logging
from telegram import Bot

logger = logging.getLogger(__name__)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def send_telegram_notification(chat_id: str, message: str):
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Token do Telegram não configurado.")
        return
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Mensagem enviada ao chat {chat_id}")
    except Exception as e:
        logger.error(f"Erro ao enviar Telegram: {e}")