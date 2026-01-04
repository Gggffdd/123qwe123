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

app = FastAPI(title="UNIVERSAL SHOP API")

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

class OrderCreate(BaseModel):
    product_id: int
    payment_method: str

# Имитация базы данных (в реальном проекте используйте PostgreSQL)
db = {
    "users": [],
    "games": [
        {"id": 1, "name": "Genshin Impact", "icon_url": "https://via.placeholder.com/100"},
        {"id": 2, "name": "Honkai: Star Rail", "icon_url": "https://via.placeholder.com/100"},
        {"id": 3, "name": "Mobile Legends", "icon_url": "https://via.placeholder.com/100"},
    ],
    "apps": [
        {"id": 1, "name": "Продвижение", "icon_url": "https://via.placeholder.com/100"},
        {"id": 2, "name": "Дизайн", "icon_url": "https://via.placeholder.com/100"},
    ],
    "products": [
        {
            "id": 1,
            "game_id": 1,
            "name": "Аккаунт AR60",
            "description": "Аккаунт с полным прохождением",
            "price": 5000,
            "image_url": "https://via.placeholder.com/300",
            "delivery_data": "Логин: genshin123\nПароль: pass123"
        },
        {
            "id": 2,
            "game_id": 2,
            "name": "Пакет Jade",
            "description": "10000 Jade и премиум предметы",
            "price": 2500,
            "image_url": "https://via.placeholder.com/300",
            "delivery_data": "Код: STAR-RAIL-CODE-123"
        },
    ]
}

# Middleware для проверки токена Telegram
def verify_telegram_token(token: str):
    # В реальном проекте здесь должна быть проверка WebApp токена
    return True

def get_current_user(authorization: str = Depends()):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization.replace("Bearer ", "")
    if not verify_telegram_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Имитация пользователя
    return User(
        telegram_id=token[:10],
        first_name="Test",
        username="test_user",
        is_admin=os.getenv("ADMIN_ID", "896706118") in token
    )

@app.get("/")
async def root():
    return {"message": "UNIVERSAL SHOP API", "status": "online"}

@app.get("/api/dashboard")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    """Получить данные для дашборда"""
    return {
        "user": current_user.dict(),
        "games": db["games"],
        "apps": db["apps"],
        "last_viewed": db["products"][0] if db["products"] else None,
        "all_products": db["products"]
    }

@app.get("/api/games/{game_id}/products")
async def get_game_products(game_id: int):
    """Получить товары для конкретной игры"""
    products = [p for p in db["products"] if p.get("game_id") == game_id]
    return products

@app.post("/api/products/{product_id}/view")
async def track_product_view(product_id: int, current_user: User = Depends(get_current_user)):
    """Отслеживание просмотра товара"""
    logger.info(f"User {current_user.telegram_id} viewed product {product_id}")
    return {"success": True, "message": "View tracked"}

@app.post("/api/orders")
async def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    """Создать новый заказ"""
    
    # Найти товар
    product = next((p for p in db["products"] if p["id"] == order_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Создать заказ
    order_id = len(db.get("orders", [])) + 1
    order = {
        "id": order_id,
        "user_id": current_user.telegram_id,
        "product_id": order_data.product_id,
        "payment_method": order_data.payment_method,
        "amount": product["price"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Отправить уведомление в группу Telegram
    await send_telegram_notification(order, product, current_user)
    
    # Вернуть ответ в зависимости от метода оплаты
    if order_data.payment_method in ["ton", "usdt"]:
        return {
            "order_id": order_id,
            "payment_url": f"https://t.me/CryptoBot?start=payment_{order_id}",
            "requires_manual_payment": False
        }
    else:  # bank_transfer
        return {
            "order_id": order_id,
            "bank_details": {
                "bank_name": "Тинькофф",
                "card_number": "5536 9137 7373 9191",
                "account_holder": "Иван Иванов"
            },
            "requires_manual_payment": True
        }

async def send_telegram_notification(order, product, user):
    """Отправить уведомление в Telegram группу"""
    # В реальном проекте здесь будет отправка через Telegram Bot API
    logger.info(f"Order notification for order #{order['id']}")
    logger.info(f"User: {user.first_name}, Product: {product['name']}, Amount: {order['amount']}")

@app.post("/api/webhook/crypto")
async def crypto_webhook(data: dict):
    """Вебхук для подтверждения криптоплатежей"""
    logger.info(f"Crypto webhook received: {data}")
    return {"status": "ok"}

@app.post("/api/webhook/telegram")
async def telegram_webhook(update: dict):
    """Вебхук для Telegram бота"""
    logger.info(f"Telegram webhook received: {update}")
    return {"status": "ok"}

# Админ эндпоинты
@app.post("/api/admin/games")
async def create_game(game_data: dict, current_user: User = Depends(get_current_user)):
    """Создать новую игру (только админ)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    game_id = len(db["games"]) + 1
    game = {
        "id": game_id,
        "name": game_data.get("name"),
        "icon_url": game_data.get("icon_url", "")
    }
    db["games"].append(game)
    return game

@app.post("/api/admin/products")
async def create_product(product_data: dict, current_user: User = Depends(get_current_user)):
    """Создать новый товар (только админ)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product_id = len(db["products"]) + 1
    product = {
        "id": product_id,
        "name": product_data.get("name"),
        "description": product_data.get("description"),
        "price": product_data.get("price"),
        "image_url": product_data.get("image_url", ""),
        "delivery_data": product_data.get("delivery_data"),
        "game_id": product_data.get("game_id"),
        "app_id": product_data.get("app_id")
    }
    db["products"].append(product)
    return product

# Health check для Vercel
@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy", "timestamp": datetime.now().isoformat()})

# Экспорт приложения для Vercel
# ВАЖНО: Эта строка должна быть в конце файла
app = app
