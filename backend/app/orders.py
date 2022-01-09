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
)  # TODO:Filter orders in responsibility with user role
async def order(user: models.User = Depends(manager), db: Session = Depends(get_db)):
    return db.query(models.Order).all()
