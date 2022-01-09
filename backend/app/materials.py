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
async def get_clothes(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Cloth).all()


@app.get("/api/v1/accessory", response_model=List[schemas.Accessory], tags=["storage"])
async def get_accessories(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return db.query(models.Accessory).all()


@app.get(
    "/api/v1/cloth/{article}",
    response_model=List[schemas.ClothStorage],
    tags=["storage"],
)
async def get_cloth_packs(
    article: int, user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    return (
        db.query(models.ClothStorage)
        .filter(models.ClothStorage.article == article)
        .all()
    )


@app.get(
    "/api/v1/accessory/{article}",
    response_model=List[schemas.AccessoryStorage],
    tags=["storage"],
)
async def get_accessory_packs(
    article: int, user: models.User = Depends(), db: Session = Depends(get_db)
):
    return (
        db.query(models.AccessoriesStorage)
        .filter(models.AccessoriesStorage.article == article)
        .all()
    )


@app.post(
    "/api/v1/accessory",
    summary="Добавить новый accessory",
    description="По факту добавить новый артикул и ассоциированные с ним данные",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "description": "Successfully created new accessory"
                    }
                }
            }
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {
                        "description": "Article already exists"
                    }
                }
            }
        }
    },
    tags=["storage"]
)
async def add_accessory(
    data: schemas.CreateNewAccessoryRequest,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Accessory)
        .filter(models.Accessory.article == data.article)
        .one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists
    new_accessory = models.Accessory(**data.dict())
    db.add(new_accessory)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new accessory"}
    )


@app.post(
    "/api/v1/cloth",
    summary="Добавить новую ткань",
    description="По факту добавить новый артикул и ассоциированные с ним данные",
    responses={
        200: {
           "description": "OK",
           "content": {
               "application/json": {
                   "example": {
                       "description": "Successfully created new cloth"
                   }
               }
           }
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {
                        "description": "Article already exists"
                    }
                }
            }
        }
    },
    tags=["storage"]
)
async def add_cloth(
        data: schemas.CreateNewClothRequest,
        user: models.User = Depends(manager),
        db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Cloth)
            .filter(models.Cloth.article == data.article)
            .one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists
    new_cloth = models.Cloth(**data.dict())
    db.add(new_cloth)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new cloth"}
    )
