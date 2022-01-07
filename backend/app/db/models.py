from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    Enum,
    ForeignKey,
    Table,
    DateTime,
    Numeric,
    Text,
    Float,
)

from sqlalchemy.sql import func

from . import Base

import enum


class UserType(enum.Enum):
    customer = enum.auto()
    manager = enum.auto()
    storage_manager = enum.auto()
    former_employee = enum.auto()
    chef = enum.auto()


class OrderStage(enum.Enum):
    waiting = enum.auto()
    accepted = enum.auto()
    rejected = enum.auto()
    done = enum.auto()


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class Cloth(Base):
    __tablename__ = "clothes"

    article = Column(Integer, primary_key=True)
    name = Column(String)
    color = Column(String)
    print = Column(String, nullable=True)
    image = Column(String, nullable=True)
    composition = Column(Text)
    width = Column(Integer)
    price = Column(Numeric(10, 2))
    base_unit = Column(Integer, ForeignKey("units.id"))


class ClothStorage(Base):
    __tablename__ = "cloth_storage"

    number = Column(Integer, primary_key=True)
    article = Column(Integer, ForeignKey("clothes.article"), primary_key=True)
    length = Column(Integer)


class Product(Base):
    __tablename__ = "products"

    article = Column(Integer, primary_key=True)

    name = Column(String)
    width = Column(Integer)
    length = Column(Integer)
    image = Column(String, nullable=True)
    comment = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    login = Column(String, unique=True)
    password = Column(LargeBinary)
    salt = Column(LargeBinary)
    role = Column(Enum(UserType))
    name = Column(String)


class Accessory(Base):
    __tablename__ = "accessories"

    article = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    width = Column(Integer)
    length = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Numeric(10, 2))


class AccessoriesStorage(Base):
    __tablename__ = "accessories_storage"

    batch = Column(Integer, primary_key=True)
    article = Column(Integer, ForeignKey("accessories.article"), primary_key=True)
    count = Column(Integer)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime, server_default=func.now())
    completion_date = Column(DateTime, nullable=True)
    stage = Column(Enum(OrderStage))
    customer = Column(Integer, ForeignKey("users.id"))
    manager = Column(Integer, ForeignKey("users.id"), nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)


ProductAccessoryRelations = Table(
    "product_accessory_relations",
    Base.metadata,
    Column("product_article", ForeignKey("products.article"), primary_key=True),
    Column("accessory_article", ForeignKey("accessories.article"), primary_key=True),
)

ProductClothRelations = Table(
    "product_cloth_relations",
    Base.metadata,
    Column("product_article", ForeignKey("products.article"), primary_key=True),
    Column("cloth_article", ForeignKey("clothes.article"), primary_key=True),
)

ProductOrderRelations = Table(
    "product_order_relations",
    Base.metadata,
    Column("product_article", ForeignKey("products.article"), primary_key=True),
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
)
