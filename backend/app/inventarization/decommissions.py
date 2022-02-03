from decimal import Decimal
from typing import Optional
import math

from ..main import app, manager
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.responses import JSONResponse
from .. import exceptions
from ..db import get_db, models


@app.patch("/api/v1/cloth/{article}/{number}", tags=["storage"])
async def cloth_decommission(
    article: int,
    number: int,
    length: float,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    if user.role not in [models.UserType.chef, models.UserType.storage_manager]:
        raise exceptions.InsufficientPrivileges
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
    if math.fabs(batch.length) < 1e-10:
        db.delete(batch)

    new_decommission = models.ClothChanges()
    new_decommission.length = length
    new_decommission.cloth_article = (article,)
    new_decommission.number = number
    new_decommission.is_income = False

    db.add(new_decommission)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


@app.patch("/api/v1/accessory/{article}", tags=["storage"])
async def accessory_decommission(
    article: int,
    quantity: int,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    if user.role not in [models.UserType.chef, models.UserType.storage_manager]:
        raise exceptions.InsufficientPrivileges
    batch: Optional[models.AccessoriesStorage] = (
        db.query(models.AccessoriesStorage)
        .filter(models.AccessoriesStorage.article == article)
        .one_or_none()
    )
    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.amount < quantity:
        raise exceptions.InsufficientAccessoryCount

    batch.amount -= quantity
    if batch.amount == 0:
        db.delete(batch)

    new_decommission = models.AccessoryChanges()
    new_decommission.amount = quantity
    new_decommission.accessory_article = article
    new_decommission.is_income = False

    db.add(new_decommission)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )


@app.patch("/api/v1/accessory_in_kg/{article}", tags=["storage"])
def accessory_in_kg_decommission(article: int, amount: float, user: models.User = Depends(manager), db: Session = Depends(get_db)):
    if user.role not in [models.UserType.chef, models.UserType.storage_manager]:
        raise exceptions.InsufficientPrivileges

    batch: Optional[models.AccessoriesStorage] = (
        db.query(models.AccessoriesStorage)
            .filter(models.AccessoriesStorage.article == article)
            .one_or_none()
    )

    accessory: models.Accessory = db.query(models.Accessory).filter(models.Accessory == article).one_or_none()

    if accessory is None:
        raise exceptions.ArticleDoesNotExist

    if not accessory.kg_acceptable:
        return JSONResponse(
            status_code= 400,
            content={
                "detail": "Cannot decommission in kg on this item"
            }
        )

    quantity = round(amount / accessory.weight)

    if batch is None:
        raise exceptions.InvalidClothStorage

    if batch.amount < quantity:
        raise exceptions.InsufficientAccessoryCount

    batch.amount -= quantity
    if batch.amount == 0:
        db.delete(batch)

    new_decommission = models.AccessoryChanges()
    new_decommission.amount = quantity
    new_decommission.accessory_article = article
    new_decommission.is_income = False

    db.add(new_decommission)
    db.commit()
    db.flush()

    return JSONResponse(
        status_code=200, content={"description": "Decommissioned successfully"}
    )