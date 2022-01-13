import json
from typing import List, Dict

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions
from .main import app, manager
from .db import models, get_db
from . import schemas


@app.get("/api/v1/order", response_model=List[schemas.Order], tags=["orders"])
async def order(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    if user.role == models.UserType.manager:
        return (
            db.query(models.OrderWithAllInfo)
            .filter(models.OrderWithAllInfo.manager_id == user.id)
            .all()
        )
    elif user.role == models.UserType.chef:
        return db.query(models.OrderWithAllInfo).all()
    else:
        ret: List[models.OrderWithAllInfo] = (
            db.query(models.OrderWithAllInfo)
            .filter(models.OrderWithAllInfo.customer_id == user.id)
            .all()
        )
        print("hmmmm: ", ret[0].products)
        return (
            ret
        )


@app.get("/api/v1/order_stages", tags=["orders"])
async def get_stages():
    return {
        "waiting": models.OrderStage.waiting,
        "accepted": models.OrderStage.accepted,
        "rejected": models.OrderStage.rejected,
        "done": models.OrderStage.done,
    }


@app.patch("/api/v1/order/{id}", tags=["orders"])
async def change_order_status(
    id: int,
    status: models.OrderStage,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    current_order: models.Order = (
        db.query(models.Order).filter(models.Order.id == id).one_or_none()
    )
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

    return JSONResponse(status_code=200)


@app.post("/api/v1/order")
async def create_order(
    products_json: str,
    user: models.User = Depends(manager),
    db: Session = Depends(get_db),
):
    if user.role != models.UserType.customer:
        raise exceptions.InsufficientPrivileges
    new_order: models.OrderWithAllInfo = models.OrderWithAllInfo(
        stage=models.OrderStage.waiting, customer_id=user.id, cost=0
    )
    db.add(new_order)
    db.flush()
    db.refresh(new_order)
    products: Dict = json.loads(products_json)
    for product, count in products.items():
        product_obj: models.ProductWithOrders = (
            db.query(models.ProductWithOrders)
            .filter(
                models.ProductWithOrders.article == product,
                models.ProductWithOrders.current_active == True,
            )
            .one()
        )
        new_order.cost += product_obj.price * count
        assoc: models.ProductOrderRelations = models.ProductOrderRelations(count=count)
        assoc.product = product_obj
        assoc.order = new_order
        new_order.products.append(assoc)


    all_managers = (
        db.query(models.ManagerWithOrders)
        .filter(models.ManagerWithOrders.role == models.UserType.manager)
        .all()
    )
    if len(all_managers) == 0:
        return JSONResponse(
            status_code=404,
            content={"description": "No managers in the system. It's matrix Neo."},
        )

    all_managers = sorted(all_managers, key=lambda x: len(x.orders))
    new_order.manager_id = all_managers[0].id

    db.commit()

    return JSONResponse(status_code=200)
