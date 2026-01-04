from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    telegram_id: str
    username: Optional[str]
    first_name: str
    last_name: Optional[str]

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Game schemas
class GameBase(BaseModel):
    name: str
    icon_url: str

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: str
    image_url: str
    price: float
    delivery_data: str
    game_id: Optional[int] = None
    app_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    is_active: bool
    is_unique: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    product_id: int
    payment_method: str  # "ton", "usdt", "bank_transfer"

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard response
class DashboardResponse(BaseModel):
    user: User
    games: List[Game]
    apps: List[App]
    last_viewed: Optional[Product]
    all_products: List[Product]

# View history
class ViewHistoryBase(BaseModel):
    product_id: int

class ViewHistory(ViewHistoryBase):
    id: int
    user_id: int
    viewed_at: datetime
    
    class Config:
        from_attributes = True
