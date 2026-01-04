import os
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Order, Product
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ORDER_GROUP_ID = int(os.getenv("ORDER_GROUP_ID"))

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Save user to database
    db = SessionLocal()
    existing_user = db.query(User).filter(User.telegram_id == str(user.id)).first()
    
    if not existing_user:
        new_user = User(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_admin=(user.id == ADMIN_ID)
        )
        db.add(new_user)
        db.commit()
    
    # Send mini app link
    keyboard = [[
        InlineKeyboardButton("🎮 Открыть магазин", web_app={"url": "https://your-domain.com"})
    ]]
    
    await update.message.reply_text(
        "Добро пожаловать в UNIVERSAL SHOP!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_order_notification(order: Order, product: Product, user: User):
    """Send order notification to group"""
    try:
        payment_methods = {
            "ton": "TON",
            "usdt": "USDT",
            "bank_transfer": "Перевод по реквизитам"
        }
        
        message = f"""
🛒 НОВЫЙ ЗАКАЗ #{order.id}

👤 Покупатель: {user.first_name} {user.last_name or ''} (@{user.username or 'N/A'})
📦 Товар: {product.name}
💰 Сумма: {order.amount} руб.
💳 Способ оплаты: {payment_methods.get(order.payment_method, order.payment_method)}
🕐 Время: {order.created_at.strftime('%d.%m.%Y %H:%M')}
        """
        
        # Create keyboard for admin actions
        keyboard = []
        if order.payment_method == "bank_transfer":
            keyboard.append([
                InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"confirm_{order.id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{order.id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("💬 Написать покупателю", 
                               url=f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.telegram_id}")
        ])
        
        # Send photo if available
        if product.image_url:
            await bot.send_photo(
                chat_id=ORDER_GROUP_ID,
                photo=product.image_url,
                caption=message,
                reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
            )
        else:
            await bot.send_message(
                chat_id=ORDER_GROUP_ID,
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
            )
            
    except Exception as e:
        logger.error(f"Failed to send order notification: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    db = SessionLocal()
    
    if data.startswith("confirm_"):
        order_id = int(data.split("_")[1])
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if order:
            order.status = "paid"
            db.commit()
            
            # Send product to user
            product = db.query(Product).filter(Product.id == order.product_id).first()
            try:
                await bot.send_message(
                    chat_id=order.user.telegram_id,
                    text=f"✅ Оплата подтверждена!\n\nВаш товар:\n{product.delivery_data}"
                )
                
                # Update message in group
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n✅ Оплата подтверждена, товар отправлен"
                )
            except Exception as e:
                logger.error(f"Failed to send product: {e}")
    
    elif data.startswith("reject_"):
        order_id = int(data.split("_")[1])
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if order:
            order.status = "cancelled"
            db.commit()
            
            try:
                await bot.send_message(
                    chat_id=order.user.telegram_id,
                    text="❌ Ваш заказ был отклонён. Свяжитесь с поддержкой для уточнения деталей."
                )
                
                await query.edit_message_caption(
                    caption=query.message.caption + "\n\n❌ Заказ отклонён"
                )
            except Exception as e:
                logger.error(f"Failed to send rejection: {e}")

def run_bot():
    """Run the Telegram bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run_bot()
