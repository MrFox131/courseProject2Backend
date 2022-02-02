from __future__ import annotations

import datetime
from typing import Optional, List, ForwardRef

from pydantic import BaseModel

from ..db import models


class Cloth(BaseModel):
    article: int
    name: str
    color: str
    print: Optional[str]
    image: Optional[str]
    composition: str
    width: float
    price: float

    class Config:
        orm_mode = True


class ClothStorage(BaseModel):
    number: int
    article: int
    length: float

    class Config:
        orm_mode = True


class Accessory(BaseModel):
    article: int
    name: str
    type: str
    width: int
    length: Optional[int] = None
    weight: Optional[float] = None
    image: Optional[str] = None
    price: Optional[float] = None
    kg_acceptable: bool

    class Config:
        orm_mode = True


class RegisterRequest(BaseModel):
    login: str
    password: str
    name: str
    role: int


class PlainLoginRequest(BaseModel):
    login: str
    password: str


class AccessoryStorage(BaseModel):
    article: int
    amount: float

    class Config:
        orm_mode = True


class AccessoryStorageWithAccessory(BaseModel):
    article: int
    amount: float
    accessory: Accessory

    class Config:
        orm_mode = True


class UserModel(BaseModel):
    login: str
    name: str
    role: models.UserType

    class Config:
        orm_mode = True


class CreateNewAccessoryRequest(BaseModel):
    article: int
    name: str
    type: str
    width: int
    length: Optional[int]
    weight: Optional[int]
    price: float


class CreateNewClothRequest(BaseModel):
    article: int
    color: str
    print: Optional[str]
    width: int
    name: str
    composition: str
    price: float


class Product(BaseModel):

    id: int
    article: int
    name: str
    width: int
    length: int
    image: Optional[str]
    comment: Optional[str]
    price: float
    clothes: Optional[List[Cloth]]
    accessories: Optional[List[Accessory]]
    previous: Optional["Product"]

    class Config:
        orm_mode = True


class ProductsContainer(BaseModel):
    product: Product

    class Config:
        orm_mode = True


class Order(BaseModel):
    id: int
    creation_date: datetime.datetime
    completion_date: Optional[datetime.datetime]
    stage: models.OrderStage
    manager: UserModel
    customer: UserModel
    cost: float
    products: Optional[List[ProductsContainer]]

    class Config:
        orm_mode = True
