from typing import Optional

from pydantic import BaseModel


class Cloth(BaseModel):
    article: int
    name: str
    color: str
    print: Optional[str]
    image: Optional[str]
    composition: str
    width: int
    price: float

    class Config:
        orm_mode = True


class ClothStorage(BaseModel):
    number: int
    article: int
    length: int

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


class RegisterRequest(BaseModel):
    login: str
    password: str
    name: str
    role: int


class PlainLoginRequest(BaseModel):
    login: str
    password: str

class AccessoryStorage(BaseModel):
    batch: int
    article: int
    count: int

    class Config:
        orm_mode = True