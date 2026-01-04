from fastapi import APIRouter, Request
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhook/telegram")
async def handle_telegram_webhook(request: Request):
    """Обработчик вебхука от Telegram"""
    data = await request.json()
    logger.info(f"Telegram webhook received: {data}")
    
    # Здесь будет обработка обновлений от Telegram
    # В реальном проекте используйте python-telegram-bot
    
    return {"ok": True}

@router.get("/webhook/telegram")
async def verify_webhook():
    """Для верификации вебхука"""
    return {"status": "webhook_set"}
