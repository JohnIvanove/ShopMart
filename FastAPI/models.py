from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    category = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    cart_items = relationship("Cart", back_populates="product")
    favorites = relationship("Favorite", back_populates="product")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    cart_items = relationship("Cart", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

class Cart(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint ("user_id", "product_id", name = "uq_user_product"),
    )
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")