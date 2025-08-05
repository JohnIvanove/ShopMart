from fastapi import APIRouter, Request, Depends, Response, HTTPException, status
from typing import Optional
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import crud, database, auth, schemas
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/product",
    tags=["product"],
)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, summary="Product detail page")
async def get_product_detail (
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: Optional[schemas.UserOut] = Depends(auth.get_optional_current_user)
):
    if current_user is None:
        return Response (
            status_code = status.HTTP_302_FOUND,
            headers = {"Location": "/account/login"}
        )
    
    # product = crud.get_product(db, product_id=product_id)
    # if not product:
    #     raise RedirectResponse (url="/products", status_code=status.HTTP_303_SEE_OTHER)
    
    product = None

    return templates.TemplateResponse(
        "partials/products/product_detail.html",
        {"request": request, "product": product, "current_user": current_user}
    )