from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions
from .main import app, manager
from .db import models, get_db
from . import schemas


@app.get("/api/v1/cloth", response_model=List[schemas.Cloth], tags=["storage"])
async def get_clothes(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    return db.query(models.Cloth).all()


@app.get("/api/v1/accessory", response_model=List[schemas.Accessory], tags=["storage"])
async def get_accessories(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    return db.query(models.Accessory).all()


@app.get("/api/v1/cloth/{article}", response_model=List[schemas.ClothStorage], tags=["storage"])
async def get_cloth_packs(article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)):
    return db.query(models.ClothStorage).filter(models.ClothStorage.article == article).all()


@app.get("/api/v1/accessory/{article}", response_model=List[schemas.AccessoryStorage], tags=["storage"])
async def get_accessory_packs(article: int, user: models.User = Depends(), db: Session = Depends(get_db)):
    return db.query(models.AccessoriesStorage).filter(models.AccessoriesStorage.article == article).all()

