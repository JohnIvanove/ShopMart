from typing import Optional
from fastapi import APIRouter, Request, Depends, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

import crud, database, schemas
from auth import get_optional_current_user

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, summary="Products page with filters")
async def products_page(
    request: Request,
    category: Optional[str] = Query(None, title="Category"),
    search: Optional[str] = Query(None, title="Search"),

    # Приймаємо як Optional[str], щоб не було 422 на порожній рядок
    raw_min_price: Optional[str] = Query(None, alias="minPrice", title="Min price"),
    raw_max_price: Optional[str] = Query(None, alias="maxPrice", title="Max price"),

    skip: int = Query(0, ge=0, title="Skip"),
    limit: int = Query(10, ge=1, title="Limit"),

    db: Session = Depends(database.get_db),
    current_user: Optional[schemas.User] = Depends(get_optional_current_user),
):
    """
    Відображає сторінку товарів.
    Для HTMX-запитів повертає тільки фрагмент сітки.
    Інакше — повний шаблон з фільтрами.
    """

    # Редирект на логін, якщо не залогінений
    if current_user is None:
        return RedirectResponse(url="/account/login", status_code=status.HTTP_302_FOUND)

    # Конвертація порожніх рядків у None
    min_price: Optional[float] = None
    if raw_min_price:
        try:
            min_price = float(raw_min_price)
        except ValueError:
            pass

    max_price: Optional[float] = None
    if raw_max_price:
        try:
            max_price = float(raw_max_price)
        except ValueError:
            pass

    # Отримуємо категорії для селектора
    categories = crud.get_category_all(db)

    # Фільтруємо товари через CRUD
    products = crud.get_products_filter(
        db,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit,
    )

    context = {
        "request": request,
        "products": products,
        "categories": categories,
        "filters": {
            "category": category or "",
            "search": search or "",
            "minPrice": raw_min_price or "",
            "maxPrice": raw_max_price or "",
            "skip": skip,
            "limit": limit,
        },
        "current_user": current_user,
    }

    # Якщо запит від HTMX — віддаємо тільки grid-фрагмент
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("partials/products/products_grid.html", context)

    # Інакше — повний layout
    return templates.TemplateResponse("products.html", context)

@router.get("/toggle-filter-label")
def toggle_label(hidden: bool = Query(True)):
    return "Show Filters" if hidden else "Hide Filters"
