from typing import List

from ..main import app, manager
from sqlalchemy.orm import Session
from fastapi import Depends
from ..db import get_db, models
from .. import schemas
from .. import exceptions


@app.get("/api/v1/get_all_items_status", response_model=List[schemas.StorageStatus])
def get_all_items_status(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    if user.role not in [models.UserType.chef, models.UserType.storage_manager]:
        raise exceptions.InsufficientPrivileges

    answer = []
    for cloth_article in db.query(models.ClothStorage.article).distinct():
        cloth: models.Cloth = db.query(models.Cloth).filter(models.Cloth.article == cloth_article).one()
        all_clothes: List[models.ClothStorage] = db.query(models.ClothStorage).filter(models.ClothStorage.article == cloth_article).all()
        area = 0.0
        for cloth_storage in all_clothes:
            area += float(cloth_storage.length*cloth.width)
        all_patches: List[models.Patch] = db.query(models.Patch).filter(models.Patch.article == cloth_article).all()

        for patch in all_patches:
            area += float(patch.width*patch.length)

        answer.append({
            "type": "cloth",
            "article": cloth_article,
            "name": cloth.name,
            "amount": area
        })

    for accessory in db.query(models.AccessoriesStorage).all():
        accessory_row: models.Accessory = db.query(models.Accessory).filter(models.Accessory.article == accessory.article).one()
        answer.append({
            "type": "accessory",
            "article": accessory_row.article,
            "name": accessory_row.name,
            "amount": accessory.amount
        })

    return answer