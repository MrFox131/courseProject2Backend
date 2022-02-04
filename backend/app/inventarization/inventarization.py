import datetime
from typing import List, Union

from fastapi.responses import JSONResponse
from functools import reduce

from ..main import app, manager
from sqlalchemy.orm import Session
from fastapi import Depends
from ..db import get_db, models
from .. import schemas
from .. import exceptions


@app.get("/api/v1/get_all_items_status", response_model=List[schemas.StorageStatus])
def get_all_items_status(
    user: models.User = Depends(manager), db: Session = Depends(get_db)
):
    if user.role not in [models.UserType.chef, models.UserType.storage_manager]:
        raise exceptions.InsufficientPrivileges

    answer = []
    for cloth_article in db.query(models.ClothStorage.article).distinct():
        cloth: models.Cloth = (
            db.query(models.Cloth).filter(models.Cloth.article == cloth_article).one()
        )
        all_clothes: List[models.ClothStorage] = (
            db.query(models.ClothStorage)
            .filter(models.ClothStorage.article == cloth_article)
            .all()
        )
        for cloth_storage in all_clothes:
            area = float(cloth_storage.length * cloth.width)
            answer.append(
                {
                    "type": "cloth_batch",
                    "batch_number": cloth_storage.number,
                    "amount": area,
                    "cloth": cloth,
                }
            )
        all_patches: List[models.Patch] = (
            db.query(models.Patch).filter(models.Patch.article == cloth_article).all()
        )

        for patch in all_patches:
            area = float(patch.width * patch.length)
            answer.append(
                {
                    "type": "cloth_patch",
                    "patch_id": patch.id,
                    "amount": area,
                    "cloth": cloth,
                }
            )

    for accessory in db.query(models.AccessoriesStorage).all():
        accessory_row: models.Accessory = (
            db.query(models.Accessory)
            .filter(models.Accessory.article == accessory.article)
            .one()
        )
        answer.append(
            {
                "type": "accessory",
                "amount": accessory.amount,
                "accessory": accessory_row,
            }
        )

    return answer


@app.post("/api/v1/new_state_after_inventarixation")  # TODO
def new_state(
    new_values: List[schemas.StorageStatus],
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    for value in new_values:
        if value.type == "accessory":
            if value.accessory.kg_acceptable:
                accessory = (
                    db.query(models.AccessoriesStorage)
                    .filter(
                        models.AccessoriesStorage.article == value.accessory.article
                    )
                    .one()
                )
                accessory.amount = round(value.amount / value.accessory.weight)
                if accessory.amount == 0:
                    db.delete(accessory)
            else:
                accessory = (
                    db.query(models.AccessoriesStorage)
                    .filter(
                        models.AccessoriesStorage.article == value.accessory.article
                    )
                    .one()
                )
                accessory.amount = int(value.amount)
                if accessory.amount == 0:
                    db.delete(accessory)
        elif value.type == "cloth_batch":
            cloth_batch: models.ClothStorage = (
                db.query(models.ClothStorage)
                .filter(
                    models.ClothStorage.article == value.cloth.article,
                    models.ClothStorage.number == value.batch_number,
                )
                .one()
            )
            cloth_batch.length = value.amount / value.cloth.width
            if cloth_batch.length <= 0.001:
                db.delete(cloth_batch)
        else:
            if value.delete_batch:
                batch = (
                    db.query(models.ClothPiece)
                    .filter(models.ClothPiece.id == value.patch_id)
                    .one()
                )
                db.delete(batch)

    db.commit()

    return JSONResponse(status_code=200, content={"detail": "Successfully"})


@app.get("/api/v1/get_changes")
def get_changes(
    start: datetime.datetime,
    end: datetime.datetime,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    if user.role != models.UserType.manager:
        raise exceptions.InsufficientPrivileges

    # cloth_changes: List[models.ClothChanges] = (
    #     db.query(models.ClothChanges)
    #     .filter(
    #         models.ClothChanges.timestamp >= start, models.ClothChanges.timestamp <= end
    #     )
    #     .all()
    # )
    # accessory_changes: List[models.AccessoryChanges] = (
    #     db.query(models.AccessoryChanges)
    #     .filter(models.AccessoryChanges.timestamp >= start, models.ClothChanges.timestamp <= end)
    #     .all()
    # )

    # cloth_changes_result = {
    #     "income": 0,
    #     "outcome": 0,
    # }
    # for i in cloth_changes:
    #     if i.is_income:
    #         cloth_changes_result["income"] += i.area
    #     else:
    #         cloth_changes_result["outcome"] += i.area
    #
    # cloth_changes_result["result"] = (
    #     cloth_changes_result["income"] - cloth_changes_result["outcome"]
    # )
    #
    # accessory_changes_result = {
    #     "income": 0,
    #     "outcome": 0,
    # }
    # for i in accessory_changes:
    #     if i.is_income:
    #         cloth_changes_result["income"] += i.amount
    #     else:
    #         cloth_changes_result["outcome"] += i.amount
    #
    # cloth_changes_result["result"] = (
    #     cloth_changes_result["income"] - cloth_changes_result["outcome"]
    # )

    cloth_articles = (
        db.query(models.ClothChanges.cloth_article)
        .filter(
            models.ClothChanges.timestamp >= start, models.ClothChanges.timestamp <= end
        )
        .distinct()
    )
    cloth_results = {}

    for cloth_article in cloth_articles:
        changes: List[models.ClothChanges] = db.query(
            models.ClothChanges.cloth_article == cloth_article
        ).all()
        for change in changes:
            if not cloth_article in cloth_results.keys():
                cloth_results[cloth_article] = {
                    "income": 0.0,
                    "outcome": 0.0,
                    "summary": 0.0,
                }
            if change.is_income:
                cloth_results[cloth_article]["income"] += change.area
            else:
                cloth_results[cloth_article]["outcome"] += change.area

        cloth_results[cloth_article]["summary"] = (
            cloth_results[cloth_article]["income"]
            - cloth_results[cloth_article]["outcome"]
        )

    accessory_articles = (
        db.query(models.AccessoryChanges.accessory_article)
            .filter(
            models.AccessoryChanges.timestamp >= start, models.AccessoryChanges.timestamp <= end
        )
            .distinct()
    )

    accessory_results = {}

    for accessory_article in accessory_articles:
        changes: List[models.AccessoryChanges] = db.query(
            models.AccessoryChanges.cloth_article == accessory_article
        ).all()
        for change in changes:
            if not accessory_article in accessory_results.keys():
                accessory_results[accessory_article] = {
                    "income": 0,
                    "outcome": 0,
                    "summary": 0,
                }
            if change.is_income:
                accessory_results[accessory_article]["income"] += change.amount
            else:
                accessory_results[accessory_article]["outcome"] += change.amount

        accessory_results[accessory_article]["summary"] = (
                accessory_results[accessory_article]["income"]
                - accessory_results[accessory_article]["outcome"]
        )

    return {"clothes": cloth_results, "accessory": accessory_results}
