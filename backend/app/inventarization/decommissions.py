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
    batch: Optional[models.AccessoriesStorage] = (
        db.query(models.AccessoriesStorage)
            .filter(models.AccessoriesStorage.article == article)
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