from fastapi import APIRouter, HTTPException, Depends, Request, Query, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud, schemas, auth
from typing import Optional
from database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin",],
)

template = Jinja2Templates(directory="templates")


@router.get ("/", response_class=HTMLResponse)
async def get_admin (request: Request, current_user: Optional[schemas.UserOut] = Depends(auth.get_optional_current_user)):
    # """
    # Get admin details for a specific user.
    # """
    # user = crud.get_user_by_id (db, user_id=user_id)
    # if current_user is None:
    #     return RedirectResponse(url="/account/login", status_code=status.HTTP_302_FOUND)
    # if not user.is_admin:
    #     raise HTTPException (status_code=403, detail="User is not an admin")
    # return user
    return template.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "current_user": current_user
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(
    request: Request,
):
    return template.TemplateResponse(
        "partials/admin/admin_dashboard.html",
        {"request": request}
    )

@router.get("/products", response_class=HTMLResponse)
async def get_products(
    request: Request,
    db: Session = Depends(get_db)
):
    
    products = crud.get_products(db)

    return template.TemplateResponse(
        "partials/admin/admin_products.html",
        {"request": request, "products": products}
    )

@router.post ("/product", response_model=schemas.User)
async def create_product (
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
    ) -> schemas.ProductCreate:
    """
    Create a new product. Only accessible by admin users.
    """    
    db_product = crud.create_product(db=db, product=product)
    return db_product

@router.get("/orders", response_class=HTMLResponse)
async def get_orders(
    request: Request,
    db: Session = Depends(get_db)
):
    # orders = crud.get_orders(db)
    orders = None

    return template.TemplateResponse(
        "partials/admin/admin_orders.html",
        {"request": request, "orders": orders}
    )

@router.get("/sidebar", response_class=HTMLResponse)
def admin_sidebar(
    request: Request,
):
    links = [
        {"name": "Dashboard", "href": "/admin/dashboard", "icon": "shapes"},
        {"name": "Products",  "href": "/admin/products", "icon": "box-open"},
        {"name": "Orders",    "href": "/admin/orders",   "icon": "shopping-bag"},
        {"name": "Users",     "href": "/admin/users",    "icon": "users"},
    ]
    return template.TemplateResponse(
        "partials/admin/admin_sidebar.html",
        {"request": request, "links": links}
    )

@router.get("/users", response_class=HTMLResponse)
async def get_users(
    request: Request,
    db: Session = Depends(get_db)
):
    # users = crud.get_users(db)
    users = None

    return template.TemplateResponse(
        "partials/admin/admin_users.html",
        {"request": request, "users": users}
    )

from datetime import datetime
from fastapi import Form

@router.post("/save/product", response_model=schemas.ProductOut)
async def save_product(
    name: str        = Form(...),
    description: str = Form(...),
    price: float     = Form(...),
    category: str    = Form(...),
    db: Session      = Depends(get_db)
):
    product_in = schemas.ProductCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        stock=0,
        created_at=datetime.utcnow()
    )
    return crud.create_product(db=db, product_in=product_in)
@router.put ("/product/{id}", response_model=schemas.UserOut)
async def update_product (
    id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
    ) -> schemas.ProductOut:
    """
    Update an existing product. Only accessible by admin users.
    """
    db_product = crud.get_product(db=db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = crud.update_product(db=db, product_id=id, product_in=product)
    return updated_product

@router.delete ("/product/{id}", response_model=schemas.ProductOut)
async def delete_product (
    id: int,
    db: Session = Depends(get_db)
    ) -> schemas.ProductOut:
    """
    Delete a product. Only accessible by admin users.
    """
    db_product = crud.get_product(db=db, product_id=id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    crud.delete_product(db=db, product_id=id)
    return {"detail": "Product deleted successfully"}