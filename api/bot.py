import os
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8317412011:AAGopoDYX69WeeDo7YpqXRkCHKkmjoTR9eg")
ADMIN_ID = int(os.getenv("ADMIN_ID", "896706118"))
ORDER_GROUP_ID = int(os.getenv("ORDER_GROUP_ID", "3605074724"))

async def start_command(update: Update, context):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем кнопку для открытия мини-приложения
    keyboard = [[{
        "text": "🎮 Открыть магазин",
        "web_app": {"url": os.getenv("FRONTEND_URL", "https://your-domain.com")}
    }]]
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в UNIVERSAL SHOP – твой персональный игровой центр!",
        reply_markup={
            "inline_keyboard": keyboard
        }
    )

async def send_order_notification(order_data: dict):
    """Отправить уведомление о заказе в группу"""
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        message = f"""
🛒 НОВЫЙ ЗАКАЗ #{order_data['id']}

👤 Покупатель: {order_data['user_name']}
📦 Товар: {order_data['product_name']}
💰 Сумма: {order_data['amount']} руб.
💳 Оплата: {order_data['payment_method']}
        """
        
        await bot.send_message(
            chat_id=ORDER_GROUP_ID,
            text=message
        )
        logger.info(f"Order notification sent to group {ORDER_GROUP_ID}")
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

def run_bot():
    """Запустить бота"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    
    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run_bot()
