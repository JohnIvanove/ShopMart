from fastapi import APIRouter, Depends, Response, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import crud, database, auth, schemas, models
from auth import get_optional_current_user

router = APIRouter(
    prefix="/account",
    tags=["account"],
)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, summary="Account page")
async def get_account_page(
    request: Request,
    db: Session = Depends (database.get_db),
    current_user: Optional[schemas.UserOut] = Depends(get_optional_current_user)
):

    if current_user is None:
        return Response (
            status_code = status.HTTP_302_FOUND,
            headers = {"Location": "/account/login"}
        )

    user = crud.get_user_by_id(db, user_id=current_user.id)
    if not user:
        return Response (
            status_code = status.HTTP_302_FOUND,
            headers = {"Location": "/"}
        )

    return templates.TemplateResponse(
        "account.html",
        {"request": request, "current_user": current_user, "user": user}
    )

@router.get("/login", response_class=HTMLResponse, summary="Authentication page")
async def get_auth_page(request: Request, current_user: Optional[schemas.User] = Depends(get_optional_current_user)):
    if current_user:
        return RedirectResponse (url = "/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request, "current_user": None})

@router.get ("/register", response_class = HTMLResponse, summary = "Registration page")
async def get_register_page (request: Request, current_user: Optional[schemas.User] = Depends(get_optional_current_user)):
    if current_user:
        return RedirectResponse (url = "/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse ("register.html", {"request": request, "current_user": None})

# ?
# @App.post ("/users/" , response_model = DbUser)
# async def create_user (user: UserCreate, db: Session = Depends (get_db)) -> DbUser:
#     db_user = User (name = user.name, age = user.age)
#     db.add (db_user)
#     db.commit()
#     db.refresh (db_user)
#     return db_user
# ?


@router.post(
    "/register",
    response_model=schemas.UserCreate,
    summary="Register a new user",
)
async def register_user(
    username: str       = Form(...),
    email: str          = Form(...),
    password: str       = Form(...),
    db: Session         = Depends(database.get_db),
) -> Response:
    # побудова Pydantic-моделі вручну
    user_in = schemas.UserCreate(name=username, email=email, password=password)

    existing = crud.get_user_by_email(db, email=user_in.email)
    if existing:
        return Response(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/account/register"},
        )

    hashed = auth.get_password_hash(user_in.password)
    new_user = models.User (name=user_in.name, email=user_in.email, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return Response(status_code=200, headers={"HX-Redirect": "/"})
@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):
    user = crud.get_user_by_email(db, email=email)
    if not user or not auth.verify_password(password, user.password):
        return Response(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"HX-Redirect": "/account/login"},
        )

    token = auth.create_access_token(data={"sub": str(user.id)})
    resp = Response(
        status_code=status.HTTP_200_OK,
        headers={"HX-Redirect": "/"},
    )
    resp.set_cookie(
        "access_token",
        token,
        httponly=True,
        path="/",
    )
    return resp

@router.get("/logout")
async def logout(request: Request):
    # Визначаємо, чи це HTMX-запит
    is_hx = request.headers.get("hx-request", "").lower() == "true"

    if is_hx:
        # HTMX чекає 200 + HX-Redirect
        response = Response(
            status_code=status.HTTP_200_OK,
            headers={"HX-Redirect": "/"},
        )
    else:
        # Класичний редірект 303
        response = RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Видаляємо кукі
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("session", path="/")

    return response