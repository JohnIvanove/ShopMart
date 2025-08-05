from fastapi import Depends, Request
from typing import List, Optional
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_password_hash


# ——————————————————————————————————————————————————————————————————
#*----------[User CRUD]----------.
# ——————————————————————————————————————————————————————————————————

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).get(user_id)

async def get_current_user(request: Request) -> Optional[int]:
    return request.session.get("user_id")

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    hashed_pw = get_password_hash(user_in.password)
    db_user = models.User(
        name=user_in.name,
        email=user_in.email,
        password=hashed_pw,
        address=user_in.address,
        image_url=user_in.image_url,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ——————————————————————————————————————————————————————————————————
#*----------[Product CRUD]----------.
# ——————————————————————————————————————————————————————————————————

def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).get(product_id)

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product_in: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product_in.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_in: schemas.ProductCreate) -> models.Product:
    db_product = db.query(models.Product).get(product_id)
    for field, value in product_in.dict().items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> None:
    db_product = db.query(models.Product).get(product_id)
    db.delete(db_product)
    db.commit()


# ——————————————————————————————————————————————————————————————————
#*----------[Category CRUD]----------.
# ——————————————————————————————————————————————————————————————————


# def get_category_by_id (db: Session, category_id: int) -> Optional[models.Category]:
#     return db.query(models.Product.category).get(category_id)

def get_category_all (db: Session) -> List[models.Product]:
    return db.query(models.Product.category).all()


from typing import Optional
from sqlalchemy.orm import Session
import models

def get_products_filter(
    db: Session,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 10,
):
    """
    Повертає товари, відфільтровані за category, search, min_price, max_price.
    Підтримує pagination через skip/limit.
    """
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category == category)

    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    return query.offset(skip).limit(limit).all()


# ——————————————————————————————————————————————————————————————————
#*----------[Filters CRUD]----------.
# ——————————————————————————————————————————————————————————————————


# def get_filters(db: Session, skip: int = 0, limit: int = 100) -> List[models.Filter]:
#     return db.query(models.Filter).offset(skip).limit(limit).all()
def create_favorite(db: Session, product_id: int, user_id: int):
    db_favorite = models.Favorite(user_id=user_id, product_id=product_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def get_favorites(db: Session, user_id: int) -> List[models.Favorite]:
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()

def delete_favorite(db: Session, product_id: int, user_id: int):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.product_id == product_id
    ).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return db_favorite


# ——————————————————————————————————————————————————————————————————
#*----------[Cart CRUD]----------.
# ——————————————————————————————————————————————————————————————————

def get_user_cart(db: Session, user_id: int) -> List[models.Cart]:
    return db.query(models.Cart).filter(models.Cart.user_id == user_id).all()

def add_item_to_cart(db: Session, user_id: int, item: schemas.CartItem) -> models.Cart:
    db_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == item.product_id
    ).first()
    if db_item:
        db_item.quantity += item.quantity
    else:
        db_item = models.Cart(
            user_id=user_id, product_id=item.product_id, quantity=item.quantity
        )
        db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_cart_item(db: Session, user_id: int, item: schemas.CartItem) -> models.Cart:
    db_item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == item.product_id
    ).first()
    if not db_item:
        raise ValueError("Item not in cart")
    db_item.quantity = item.quantity
    db.commit()
    db.refresh(db_item)
    return db_item

def remove_cart_item(db: Session, user_id: int, product_id: int) -> None:
    db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id
    ).delete()
    db.commit()
