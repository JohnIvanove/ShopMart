from fastapi import APIRouter, Request, Depends, Response, status
from typing import Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import crud
import database
import auth
import schemas

router = APIRouter(
    prefix="/cart",
    tags=["cart"],
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, summary="Cart page")
async def get_cart_page(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: Optional [schemas.UserOut] = Depends(auth.get_optional_current_user)
):
    # Якщо не залогінені — редірект на форму входу
    if current_user is None:
        return RedirectResponse(url="/account/login", status_code=status.HTTP_302_FOUND)

    # Беремо товари з корзини користувача
    cart_items = crud.get_user_cart(db, user_id=current_user.id)

    return templates.TemplateResponse(
        "cart.html",
        {"request": request, "current_user": current_user, "cart_items": cart_items}
    )
