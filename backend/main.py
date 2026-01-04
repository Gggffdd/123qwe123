from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import SessionLocal, engine, Base
from models import User, Game, App, Product, Order, ViewHistory
from schemas import *
from telegram_bot import bot, send_order_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="UNIVERSAL SHOP API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

security = HTTPBearer()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    user = db.query(User).filter(User.telegram_id == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

@app.get("/")
async def root():
    return {"message": "UNIVERSAL SHOP API"}

@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard with games, apps, and view history"""
    # Get games
    games = db.query(Game).filter(Game.is_active == True).all()
    
    # Get apps
    apps = db.query(App).filter(App.is_active == True).all()
    
    # Get view history
    view_history = (
        db.query(ViewHistory)
        .filter(ViewHistory.user_id == current_user.id)
        .order_by(ViewHistory.viewed_at.desc())
        .first()
    )
    
    # Get all products mixed
    all_products = db.query(Product).filter(Product.is_active == True).all()
    
    return {
        "user": current_user,
        "games": games,
        "apps": apps,
        "last_viewed": view_history.product if view_history else None,
        "all_products": all_products
    }

@app.get("/api/games/{game_id}/products")
async def get_game_products(
    game_id: int,
    db: Session = Depends(get_db)
):
    """Get all products for a specific game"""
    products = (
        db.query(Product)
        .filter(Product.game_id == game_id, Product.is_active == True)
        .all()
    )
    return products

@app.post("/api/products/{product_id}/view")
async def track_product_view(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track when user views a product"""
    # Remove previous entry for this product
    db.query(ViewHistory).filter(
        ViewHistory.user_id == current_user.id,
        ViewHistory.product_id == product_id
    ).delete()
    
    # Add new view
    view = ViewHistory(
        user_id=current_user.id,
        product_id=product_id
    )
    db.add(view)
    db.commit()
    return {"success": True}

@app.delete("/api/view-history/{product_id}")
async def delete_view_history(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete specific product from view history"""
    deleted = db.query(ViewHistory).filter(
        ViewHistory.user_id == current_user.id,
        ViewHistory.product_id == product_id
    ).delete()
    db.commit()
    return {"success": deleted > 0}

@app.post("/api/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    product = db.query(Product).filter(Product.id == order_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create order
    order = Order(
        user_id=current_user.id,
        product_id=order_data.product_id,
        payment_method=order_data.payment_method,
        amount=product.price,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Send notification to Telegram group
    await send_order_notification(order, product, current_user)
    
    # If crypto payment, generate payment link
    if order_data.payment_method in ["ton", "usdt"]:
        payment_url = generate_crypto_payment_link(order, product.price)
        return {
            "order_id": order.id,
            "payment_url": payment_url,
            "requires_manual_payment": False
        }
    else:  # Bank transfer
        return {
            "order_id": order.id,
            "bank_details": get_bank_details(),
            "requires_manual_payment": True
        }

@app.post("/api/webhook/crypto")
async def crypto_webhook(payment_data: dict):
    """Webhook for crypto payment confirmation"""
    # Verify payment
    if verify_crypto_payment(payment_data):
        order_id = payment_data.get("order_id")
        db = SessionLocal()
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = "paid"
            db.commit()
            
            # Send product data to user
            product = db.query(Product).filter(Product.id == order.product_id).first()
            await send_product_to_user(order.user.telegram_id, product.delivery_data)
        db.close()
    
    return {"status": "ok"}

# Admin endpoints
@app.post("/api/admin/games")
async def create_game(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new game (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    game = Game(**game_data.dict())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@app.post("/api/admin/products")
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new product (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.put("/api/admin/orders/{order_id}/complete")
async def complete_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark order as completed (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "completed"
    db.commit()
    
    # Send product to user if not sent yet
    if order.payment_method == "bank_transfer" and order.status == "paid":
        product = db.query(Product).filter(Product.id == order.product_id).first()
        await send_product_to_user(order.user.telegram_id, product.delivery_data)
    
    return {"success": True}

def generate_crypto_payment_link(order: Order, amount: float) -> str:
    """Generate payment link for crypto"""
    # Implementation for TON/USDT payment
    return f"https://t.me/CryptoBot?start=payment_{order.id}"

def verify_crypto_payment(payment_data: dict) -> bool:
    """Verify crypto payment"""
    # Implementation for verifying crypto transactions
    return True

def get_bank_details() -> dict:
    """Get bank details for manual transfer"""
    return {
        "bank_name": "Тинькофф",
        "card_number": "5536 9137 1234 5678",
        "account_holder": "Иван Иванов"
    }

async def send_product_to_user(telegram_id: int, product_data: str):
    """Send product data to user via Telegram"""
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=f"🎉 Ваш товар успешно оплачен!\n\nДанные для получения:\n{product_data}\n\nСпасибо за покупку!"
        )
    except Exception as e:
        logger.error(f"Failed to send product to user {telegram_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
