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


@app.get(
    "/api/v1/order", response_model=List[schemas.Order], tags=["orders"]
)
async def order(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    if user.role == models.UserType.manager:
        return db.query(models.OrderWithUsers).filter(models.OrderWithUsers.manager_id == user.id).all()
    elif user.role == models.UserType.chef:
        return db.query(models.OrderWithUsers).all()
    else:
        return db.query(models.OrderWithUsers).filter(models.OrderWithUsers.customer_id == user.id).all



