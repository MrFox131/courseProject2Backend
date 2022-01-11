import json
import math
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi import Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions
from .main import app, manager
from .db import models, get_db
from . import schemas
from . import utils


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
    article: int = Depends(), user: models.User = Depends(manager), db: Session = Depends(get_db)
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
    article: int = Depends(), user: models.User = Depends(), db: Session = Depends(get_db)
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
                    "example": {"description": "Successfully created new accessory"}
                }
            },
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {"description": "Article already exists"}
                }
            },
        },
    },
    tags=["storage"],
)
async def add_accessory(
    article: int = Form(...),
    name: str = Form(...),
    type: str = Form(...),
    width: int = Form(...),
    length: Optional[int] = Form(...),
    weight: Optional[int] = Form(...),
    price: float = Form(...),
    user: models.User = Depends(manager),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Accessory)
        .filter(models.Accessory.article == article)
        .one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists

    image_filename = await utils.save_file(image)

    new_accessory = models.Accessory(
        article=article,
        name=name,
        type=type,
        width=width,
        length=length,
        weight=weight,
        price=price,
        image=image_filename,
    )
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
                    "example": {"description": "Successfully created new cloth"}
                }
            },
        },
        409: {
            "description": "Article already exists",
            "content": {
                "application/json": {
                    "example": {"description": "Article already exists"}
                }
            },
        },
    },
    tags=["storage"],
)
async def add_cloth(
    article: int = Form(...),
    color: str = Form(...),
    print: Optional[str] = Form(...),
    width: float = Form(...),
    name: str = Form(...),
    composition: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    same_article = (
        db.query(models.Cloth).filter(models.Cloth.article == article).one_or_none()
    )
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists

    image_filename = await utils.save_file(image)

    new_cloth = models.Cloth(
        article=article,
        color=color,
        print=print,
        width=width,
        name=name,
        composition=composition,
        price=price,
        image=image_filename,
    )
    db.add(new_cloth)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new cloth"}
    )


@app.patch("/api/v1/cloth/{article}/{number}", tags=["storage"])
async def cloth_decommission(
    article: int,
    number: int,
    length: float,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    batch: Optional[models.ClothStorage] = (
        db.query(models.ClothStorage)
        .filter(
            models.ClothStorage.article == article, models.ClothStorage.number == number
        )
        .one_or_none()
    )
    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.length < length:
        raise exceptions.InsufficientClothLength

    batch.length -= length
    if math.fabs(batch.length) < 1E-10:
        db.delete(batch)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


@app.patch("/api/v1/accessory/{article}/{number}", tags=["storage"])
async def accessory_decommission(
    article: int,
    number: int,
    quantity: int,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    batch: Optional[models.AccessoriesStorage] = (
        db.query(models.AccessoriesStorage)
        .filter(
            models.AccessoriesStorage.article == article,
            models.AccessoriesStorage.number == number,
        )
        .one_or_none()
    )
    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.count < quantity:
        raise exceptions.InsufficientClothLength

    batch.count -= quantity
    if batch.count == 0:
        db.delete(batch)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


@app.post("/api/v1/product", description="Добавляем новую продукцию")
async def add_new_product(article: int = Form(...), name: str = Form(...), price: float = Form(...), width: int = Form(...), length: int = Form(...), comment: str = Form(...), image: UploadFile = File(...), cloth_articles: str = Form(...), accessory_articles: str = Form(...), user: models.User = Depends(manager), db: Session = Depends(get_db)):
    same_article = db.query(models.Product).filter(models.Product.article == article).one_or_none()
    if same_article is not None:
        raise exceptions.ArticleAlreadyExists

    new_product: models.Product = models.Product()
    new_product.article = article
    new_product.name = name
    new_product.length = length
    new_product.width = width
    image_filename = utils.save_file(image)
    new_product.image = image_filename
    new_product.comment = comment
    new_product.price = price
    db.add(new_product)

    cloth_articles = json.loads(cloth_articles)
    accessory_articles = json.loads(accessory_articles)

    for cloth in cloth_articles:
        db.add(models.ProductClothRelations(product_articl=new_product.article, cloth_article=cloth))

    for accessory in accessory_articles:
        db.add(models.ProductClothRelations(product_articl=new_product.article, accessory_article=accessory))

    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Product created successfully"}
    )

