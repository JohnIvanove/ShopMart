# main.py
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from routes import account, products, product, cart, admin
import schemas, crud, database, auth
from sqlalchemy.orm import Session

# Initialize the database
database.Base.metadata.create_all(bind=database.engine)

App = FastAPI()

# 1) ПІДКЛЮЧАЄМО SESSION MIDDLEWARE ПЕРЕД ВСІМА РОУТАМИ
App.add_middleware(
    SessionMiddleware,
    secret_key="твій_секретний_ключ_тут",  # заміни на довгий випадковий рядок
    session_cookie="session",
    max_age=14 * 24 * 60 * 60
)

App.include_router (account.router, tags = ["account"])
App.include_router (products.router, tags = ["products"])
App.include_router (product.router, tags = ["product"])
App.include_router (cart.router, tags = ["cart"])
App.include_router (admin.router, tags = ["admin"])


App.mount ("/static", StaticFiles (directory = "static"), name = "static")

# 2) ШАБЛОНІЗАТОР
templates = Jinja2Templates(directory="templates")

# 4) Головна сторінка
@App.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    current_user: Optional[schemas.User] = Depends(auth.get_optional_current_user)
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user
        }
    )
