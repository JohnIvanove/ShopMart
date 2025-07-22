from fastapi import FastAPI, Request, HTTPException, Path, Query, Body, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware

from models import Base, User, Post
from database import engine, session_local
from shemas import UserCreate, User as DbUser

App = FastAPI()

templates = Jinja2Templates(directory="templates")

@App.get("/", response_class=HTMLResponse)
async def home (request: Request):
    return templates.TemplateResponse ("index.html", {"request": request})

@App.get("/items", response_class=HTMLResponse)
async def read_items(request: Request, query: str = ""):
    #? Уявна база даних
    all_items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    filtered = [item for item in all_items if query.lower() in item.lower()]

    return templates.TemplateResponse(
        "items.html",
        {"request": request, "items": filtered}
    )
