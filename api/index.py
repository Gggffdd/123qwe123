from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="UNIVERSAL SHOP API",
    description="API для универсального магазина игровых товаров и Telegram услуг",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели Pydantic
class User(BaseModel):
    telegram_id: str
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    is_admin: bool = False

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    game_id: Optional[int] = None
    app_id: Optional[int] = None
    delivery_data: str

class Game(BaseModel):
    id: int
    name: str
    icon_url: str
    is_active: bool = True

class App(BaseModel):
    id: int
    name: str
    icon_url: str
    is_active: bool = True

class OrderCreate(BaseModel):
    product_id: int
    payment_method: str

class ViewHistory(BaseModel):
    product_id: int

# Имитация базы данных
db = {
    "users": [],
    "games": [
        {"id": 1, "name": "Genshin Impact", "icon_url": "https://via.placeholder.com/100", "is_active": True},
        {"id": 2, "name": "Honkai: Star Rail", "icon_url": "https://via.placeholder.com/100", "is_active": True},
        {"id": 3, "name": "Mobile Legends", "icon_url": "https://via.placeholder.com/100", "is_active": True},
    ],
    "apps": [
        {"id": 1, "name": "Продвижение Telegram", "icon_url": "https://via.placeholder.com/100", "is_active": True},
        {"id": 2, "name": "Дизайн каналов", "icon_url": "https://via.placeholder.com/100", "is_active": True},
        {"id": 3, "name": "NFT Подарки", "icon_url": "https://via.placeholder.com/100", "is_active": True},
    ],
    "products": [
        {
            "id": 1,
            "game_id": 1,
            "name": "Аккаунт AR60",
            "description": "Премиум аккаунт с полным прохождением и всеми персонажами",
            "price": 5000.0,
            "image_url": "https://via.placeholder.com/300x200/4F46E5/FFFFFF?text=Genshin+Impact",
            "delivery_data": "Логин: genshin_premium\nПароль: securepass123\nEmail: account@example.com"
        },
        {
            "id": 2,
            "game_id": 2,
            "name": "Пакет Jade x10000",
            "description": "Большой пакет валюты + эксклюзивные предметы",
            "price": 2500.0,
            "image_url": "https://via.placeholder.com/300x200/7C3AED/FFFFFF?text=Star+Rail",
            "delivery_data": "Код активации: HSR-CODE-789XYZ-2024\nСрок действия: 30 дней"
        },
        {
            "id": 3,
            "app_id": 1,
            "name": "Продвижение канала",
            "description": "Накрутка подписчиков + просмотров на 1 месяц",
            "price": 1500.0,
            "image_url": "https://via.placeholder.com/300x200/10B981/FFFFFF?text=Promotion",
            "delivery_data": "Для активации напишите @admin с номером заказа"
        },
    ],
    "view_history": [],
    "orders": []
}

# Middleware для проверки токена Telegram
def verify_telegram_token(token: str):
    """Проверка токена Telegram WebApp"""
    try:
        # В реальном проекте здесь должна быть полная проверка подписи
        # Для демо просто проверяем, что токен не пустой
        return bool(token and len(token) > 10)
    except:
        return False

def get_current_user(authorization: str = None):
    """Получение текущего пользователя"""
    if not authorization or not authorization.startswith("Bearer "):
        # Для демо создаем тестового пользователя
        return User(
            telegram_id="123456789",
            first_name="Демо",
            username="demo_user",
            is_admin=False
        )
    
    token = authorization.replace("Bearer ", "")
    if not verify_telegram_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Извлекаем Telegram ID из токена (в реальном проекте это будет JWT или подобное)
    telegram_id = token[:10] if len(token) > 10 else "000000000"
    
    return User(
        telegram_id=telegram_id,
        first_name="Пользователь",
        username="telegram_user",
        is_admin=str(os.getenv("ADMIN_ID", "896706118")) == telegram_id
    )

@app.get("/")
async def root():
    return {
        "message": "UNIVERSAL SHOP API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "games": "/api/games",
            "products": "/api/products",
            "orders": "/api/orders"
        }
    }

@app.get("/api/dashboard")
async def get_dashboard(authorization: Optional[str] = None):
    """Получить данные для дашборда"""
    try:
        current_user = get_current_user(authorization)
        
        # Получаем последний просмотренный товар
        last_viewed = None
        if db["view_history"]:
            last_product_id = db["view_history"][-1]["product_id"]
            last_viewed = next((p for p in db["products"] if p["id"] == last_product_id), None)
        
        return {
            "user": current_user.dict(),
            "games": [g for g in db["games"] if g["is_active"]],
            "apps": [a for a in db["apps"] if a["is_active"]],
            "last_viewed": last_viewed,
            "all_products": [p for p in db["products"] if p.get("is_active", True)]
        }
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/games")
async def get_games():
    """Получить список всех игр"""
    return [g for g in db["games"] if g["is_active"]]

@app.get("/api/apps")
async def get_apps():
    """Получить список всех приложений"""
    return [a for a in db["apps"] if a["is_active"]]

@app.get("/api/games/{game_id}/products")
async def get_game_products(game_id: int):
    """Получить товары для конкретной игры"""
    products = [p for p in db["products"] if p.get("game_id") == game_id and p.get("is_active", True)]
    return products

@app.get("/api/apps/{app_id}/products")
async def get_app_products(app_id: int):
    """Получить товары для конкретного приложения"""
    products = [p for p in db["products"] if p.get("app_id") == app_id and p.get("is_active", True)]
    return products

@app.get("/api/products")
async def get_all_products():
    """Получить все товары"""
    return [p for p in db["products"] if p.get("is_active", True)]

@app.post("/api/products/{product_id}/view")
async def track_product_view(product_id: int, authorization: Optional[str] = None):
    """Отслеживание просмотра товара"""
    try:
        current_user = get_current_user(authorization)
        
        # Удаляем старую запись для этого товара
        db["view_history"] = [vh for vh in db["view_history"] 
                             if not (vh["user_id"] == current_user.telegram_id and vh["product_id"] == product_id)]
        
        # Добавляем новую запись
        db["view_history"].append({
            "user_id": current_user.telegram_id,
            "product_id": product_id,
            "viewed_at": datetime.now().isoformat()
        })
        
        logger.info(f"User {current_user.telegram_id} viewed product {product_id}")
        return {"success": True, "message": "View tracked"}
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/view-history/{product_id}")
async def delete_view_history(product_id: int, authorization: Optional[str] = None):
    """Удалить товар из истории просмотров"""
    try:
        current_user = get_current_user(authorization)
        
        initial_count = len(db["view_history"])
        db["view_history"] = [vh for vh in db["view_history"] 
                             if not (vh["user_id"] == current_user.telegram_id and vh["product_id"] == product_id)]
        
        deleted = initial_count - len(db["view_history"])
        return {"success": deleted > 0, "deleted_count": deleted}
    except Exception as e:
        logger.error(f"Error deleting view history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders")
async def create_order(order_data: OrderCreate, authorization: Optional[str] = None):
    """Создать новый заказ"""
    try:
        current_user = get_current_user(authorization)
        
        # Найти товар
        product = next((p for p in db["products"] if p["id"] == order_data.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Создать заказ
        order_id = len(db["orders"]) + 1
        order = {
            "id": order_id,
            "user_id": current_user.telegram_id,
            "user_name": current_user.first_name,
            "product_id": order_data.product_id,
            "product_name": product["name"],
            "payment_method": order_data.payment_method,
            "amount": product["price"],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        db["orders"].append(order)
        
        # Отправить уведомление в группу Telegram
        await send_telegram_notification(order, product, current_user)
        
        # Вернуть ответ в зависимости от метода оплаты
        if order_data.payment_method in ["ton", "usdt"]:
            return {
                "order_id": order_id,
                "payment_url": f"https://t.me/CryptoBot?start=payment_{order_id}_{int(product['price'])}",
                "requires_manual_payment": False,
                "crypto_amount": product["price"],
                "crypto_currency": "TON" if order_data.payment_method == "ton" else "USDT"
            }
        else:  # bank_transfer
            return {
                "order_id": order_id,
                "bank_details": {
                    "bank_name": "Тинькофф",
                    "card_number": "5536 9137 7373 9191",
                    "account_holder": "Иван Иванов",
                    "phone": "+7 (999) 123-45-67"
                },
                "requires_manual_payment": True,
                "amount_rub": product["price"],
                "comment": f"Оплата заказа #{order_id}"
            }
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_telegram_notification(order, product, user):
    """Отправить уведомление в Telegram группу"""
    try:
        import requests
        
        TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        ORDER_GROUP_ID = os.getenv("ORDER_GROUP_ID", "3605074724")
        
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not set, skipping notification")
            return
        
        payment_methods = {
            "ton": "TON",
            "usdt": "USDT (TRC20)",
            "bank_transfer": "Перевод по реквизитам"
        }
        
        message = f"""
🛒 *НОВЫЙ ЗАКАЗ* #{order['id']}

👤 *Покупатель:* {user.first_name} {user.last_name or ''}
📱 @{user.username or 'без username'}

📦 *Товар:* {product['name']}
💰 *Сумма:* {order['amount']} ₽
💳 *Способ оплаты:* {payment_methods.get(order['payment_method'], order['payment_method'])}
🕐 *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M')}

*Статус:* {order['status']}
        """
        
        # Отправляем сообщение в группу
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ORDER_GROUP_ID,
            "text": message,
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [[
                    {
                        "text": "✅ Подтвердить оплату",
                        "callback_data": f"confirm_{order['id']}"
                    },
                    {
                        "text": "💬 Написать",
                        "url": f"https://t.me/{user.username}" if user.username else f"tg://user?id={user.telegram_id}"
                    }
                ]]
            }
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"Telegram notification sent for order #{order['id']}")
        else:
            logger.error(f"Failed to send Telegram notification: {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")

@app.post("/api/webhook/crypto")
async def crypto_webhook(data: dict):
    """Вебхук для подтверждения криптоплатежей"""
    logger.info(f"Crypto webhook received: {data}")
    
    # В реальном проекте здесь будет проверка подписи и обработка платежа
    if data.get("status") == "success":
        order_id = data.get("order_id")
        if order_id:
            # Находим заказ и обновляем статус
            for order in db["orders"]:
                if order["id"] == order_id:
                    order["status"] = "paid"
                    order["paid_at"] = datetime.now().isoformat()
                    
                    # Находим товар и отправляем данные пользователю
                    product = next((p for p in db["products"] if p["id"] == order["product_id"]), None)
                    if product:
                        logger.info(f"Order #{order_id} paid, product data: {product['delivery_data'][:50]}...")
                    
                    break
    
    return {"status": "ok", "message": "Webhook processed"}

@app.post("/api/webhook/telegram")
async def telegram_webhook(update: dict):
    """Вебхук для Telegram бота"""
    logger.info(f"Telegram webhook received: {update.get('update_id')}")
    
    # Обработка callback query
    if "callback_query" in update:
        callback = update["callback_query"]
        data = callback.get("data", "")
        
        if data.startswith("confirm_"):
            order_id = int(data.split("_")[1])
            
            # Находим заказ
            for order in db["orders"]:
                if order["id"] == order_id:
                    order["status"] = "completed"
                    order["completed_at"] = datetime.now().isoformat()
                    
                    # Отправляем подтверждение
                    import requests
                    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
                    
                    if TELEGRAM_BOT_TOKEN:
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery",
                            json={
                                "callback_query_id": callback["id"],
                                "text": f"Заказ #{order_id} подтвержден!"
                            }
                        )
                    
                    break
    
    return {"ok": True}

# Админ эндпоинты
@app.post("/api/admin/games")
async def create_game(game_data: dict, authorization: Optional[str] = None):
    """Создать новую игру (только админ)"""
    try:
        current_user = get_current_user(authorization)
        
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        game_id = len(db["games"]) + 1
        game = {
            "id": game_id,
            "name": game_data.get("name", ""),
            "icon_url": game_data.get("icon_url", ""),
            "is_active": True
        }
        db["games"].append(game)
        
        logger.info(f"Admin {current_user.telegram_id} created game: {game['name']}")
        return game
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/apps")
async def create_app(app_data: dict, authorization: Optional[str] = None):
    """Создать новое приложение (только админ)"""
    try:
        current_user = get_current_user(authorization)
        
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        app_id = len(db["apps"]) + 1
        app = {
            "id": app_id,
            "name": app_data.get("name", ""),
            "icon_url": app_data.get("icon_url", ""),
            "is_active": True
        }
        db["apps"].append(app)
        
        logger.info(f"Admin {current_user.telegram_id} created app: {app['name']}")
        return app
    except Exception as e:
        logger.error(f"Error creating app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/products")
async def create_product(product_data: dict, authorization: Optional[str] = None):
    """Создать новый товар (только админ)"""
    try:
        current_user = get_current_user(authorization)
        
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        product_id = len(db["products"]) + 1
        product = {
            "id": product_id,
            "name": product_data.get("name", ""),
            "description": product_data.get("description", ""),
            "price": float(product_data.get("price", 0)),
            "image_url": product_data.get("image_url", ""),
            "delivery_data": product_data.get("delivery_data", ""),
            "game_id": product_data.get("game_id"),
            "app_id": product_data.get("app_id"),
            "is_active": True
        }
        db["products"].append(product)
        
        logger.info(f"Admin {current_user.telegram_id} created product: {product['name']}")
        return product
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/orders/{order_id}/complete")
async def complete_order(order_id: int, authorization: Optional[str] = None):
    """Завершить заказ (только админ)"""
    try:
        current_user = get_current_user(authorization)
        
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Находим заказ
        order = next((o for o in db["orders"] if o["id"] == order_id), None)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order["status"] = "completed"
        order["completed_at"] = datetime.now().isoformat()
        
        logger.info(f"Admin {current_user.telegram_id} completed order #{order_id}")
        return {"success": True, "order_id": order_id}
    except Exception as e:
        logger.error(f"Error completing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/orders")
async def get_all_orders(authorization: Optional[str] = None):
    """Получить все заказы (только админ)"""
    try:
        current_user = get_current_user(authorization)
        
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return db["orders"]
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check для Vercel
@app.get("/health")
async def health_check():
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "universal-shop-api",
        "version": "1.0.0"
    })

# Важно: Vercel ожидает переменную `app`
# Это стандартный способ экспорта для Vercel Python runtime
app = app
