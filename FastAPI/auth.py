from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Request
import schemas, crud, database


def get_password_hash(password: str) -> str:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# auth.py
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    auto_error=False      # <- дуже важливо
)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> Optional[schemas.UserOut]:
    if not token:
        # замість HTTPException просто вертаємо None
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    user = crud.get_user_by_id(db, user_id=int(user_id))
    return user

    
async def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

async def get_optional_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(database.get_db),
) -> Optional[schemas.UserOut]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user = crud.get_user_by_id(db, user_id=int(user_id))
        if user is None:
            return None
        return user
    except JWTError:
        return None
