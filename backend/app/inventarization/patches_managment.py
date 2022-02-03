from ..main import app, manager
from sqlalchemy.orm import Session
from fastapi import Depends
from ..db import get_db, models
from .. import schemas
from .. import exceptions


@app.post("/api/v1/patch", response_model=schemas.Patch)
async def create_patch(patch: schemas.Patch, user: models.User = Depends(manager), db: Session = Depends(get_db)):
    if user.role not in [models.UserType.storage_manager, models.UserType.chef]:
        raise exceptions.InsufficientPrivileges

    new_patch = models.Patch(**(patch.dict()))

    new_income = models.ClothChanges()
    new_income.is_income = True
    new_income.cloth_article = new_patch.article
    new_income.area = new_patch.width * new_patch.length

    db.add(new_patch)
    db.add(new_income)
    db.refresh(new_patch)
    db.commit()

    return new_patch


def get_all_patches_of_article(article: int, db: Session):
    return db.query(models.Patch).filter(models.Patch.article == article).all()
