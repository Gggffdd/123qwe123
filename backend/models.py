from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    orders = relationship("Order", back_populates="user")
    view_history = relationship("ViewHistory", back_populates="user")

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    icon_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    products = relationship("Product", back_populates="game")

class App(Base):
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    icon_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    products = relationship("Product", back_populates="app")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=True)
    name = Column(String, index=True)
    description = Column(Text)
    image_url = Column(String)
    price = Column(Float)
    delivery_data = Column(Text)  # Логин:пароль или инструкция
    is_active = Column(Boolean, default=True)
    is_unique = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    game = relationship("Game", back_populates="products")
    app = relationship("App", back_populates="products")
    orders = relationship("Order", back_populates="product")
    view_history = relationship("ViewHistory", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    payment_method = Column(String)  # "ton", "usdt", "bank_transfer"
    amount = Column(Float)
    status = Column(String, default="pending")  # pending, paid, completed, cancelled
    crypto_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

class ViewHistory(Base):
    __tablename__ = "view_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="view_history")
    product = relationship("Product", back_populates="view_history")
