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


@app.get("/api/v1/order_stages", tags=["orders"])
async def get_stages():
    return {
        "waiting": models.OrderStage.waiting,
        "accepted": models.OrderStage.accepted,
        "rejected": models.OrderStage.rejected,
        "done": models.OrderStage.done
    }


@app.patch("/api/v1/order/{id}", tags=["orders"])
async def change_order_status(id: int, status: models.OrderStage, user: models.User = Depends(manager), db: Session = Depends(get_db)):
    current_order: models.Order = db.query(models.Order).filter(models.Order.id == id).one_or_none()
    if current_order is None:
        raise exceptions.OrderDoesNotExists

    if user.role == models.UserType.chef:
        current_order.stage = status
    elif user.role == models.UserType.manager:
        if current_order.manager_id != user.id:
            raise exceptions.InsufficientPrivileges
        current_order.stage = status
    else:
        raise exceptions.InsufficientPrivileges

    db.commit()

    return JSONResponse(
        status_code=200
    )