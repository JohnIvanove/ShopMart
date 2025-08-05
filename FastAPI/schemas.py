#Імпорт модулів.
from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr
from typing import Optional, List
# ——————————————————————————————————————————————————————————————————
#*----------[Створення класів користувача]----------.
# ——————————————————————————————————————————————————————————————————


# 1) Загальні поля
class UserBase (BaseModel):
    model_config = ConfigDict (from_attributes = True)
    name: str = Field (..., min_length = 2, max_length = 50)
    email: EmailStr
    address: str = Field ("Unknown", max_length = 100)
    is_admin: bool = Field (False, description = "Показує, чи є користувач адміністратором")

# 2) Для створення
class UserCreate (UserBase):
    password: str = Field (..., min_length = 8, max_length = 100)

# 3) Для віддачі
class UserOut (UserBase):
    model_config = ConfigDict (from_attributes = True)
    id: int

# 4) Для оновлення
class UserUpdate (BaseModel):
    model_config = ConfigDict (from_attributes = True)

    name: str | None = Field (
        None, min_length = 2, max_length = 50, description = "Оновлене ім'я користувача"
    )
    email: EmailStr | None = Field (None, description = "Оновлений email")
    password: str | None = Field (
        None, min_length = 8, max_length = 100, description = "Оновлений пароль"
    )
    image_url: str | None = Field (None, max_length = 255, description = "Оновлена URL картинки")
    address: str | None = Field (None, max_length = 100, description = "Оновлена адреса")


class User (UserBase):
    id: int

    class Config:
        from_attributes = True


# ——————————————————————————————————————————————————————————————————
#*----------[Створення класів продукту]----------.
# ——————————————————————————————————————————————————————————————————


class ProductBase (BaseModel):
    name: str = Field (..., min_length = 2, max_length = 50)
    description: Optional [str] = None
    price: float = Field (..., ge = 0)
    category: Optional [str] = None #?constr (max_length = 50)
    stock: int = Field (..., ge = 0)
    image_url: Optional [str] = Field (None, max_length = 255, description = "URL картинки продукту")

class ProductCreate (ProductBase):
    created_at: str = Field (..., ge = 0)

class ProductUpdate (ProductBase):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None  #?constr(max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=255, description="URL картинки продукту")
    created_at: Optional [str] = Field (None, ge = 0)

class ProductOut (ProductBase):
    id: int

    class Config:
        from_attributes = True


# ——————————————————————————————————————————————————————————————————
#*----------[Створення класу улюблених корзини]----------.
# ——————————————————————————————————————————————————————————————————


class FavoriteBase (BaseModel):
    product_id: int

class FavoriteCreate (FavoriteBase):
    pass

class FavoriteOut (FavoriteBase):
    id: int
    product: ProductOut
    class Config:
        orm_mode = True


# ——————————————————————————————————————————————————————————————————
#*----------[Створення класу елементу корзини]----------.
# ——————————————————————————————————————————————————————————————————

class CartItem (BaseModel):
    product_id: int
    quantity: int = Field (..., ge = 1)


# ——————————————————————————————————————————————————————————————————
#*----------[Створення класу Auth / JWT]----------.
# ——————————————————————————————————————————————————————————————————

class Token (BaseModel):
    access_token: str
    token_type: str