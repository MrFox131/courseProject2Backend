from pydantic import BaseModel
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
    Boolean,
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

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


ProductAccessoryRelations = Table(
    "product_accessory_relations",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("accessory_article", ForeignKey("accessories.article"), primary_key=True),
)

ProductClothRelations = Table(
    "product_cloth_relations",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("cloth_article", ForeignKey("clothes.article"), primary_key=True),
)


class ProductOrderRelations(Base):
    __tablename__ = "product_order_relations"
    product_id = Column(
        ForeignKey("products.id"), primary_key=True, autoincrement=False
    )
    order_id = Column(ForeignKey("orders.id"), primary_key=True, autoincrement=False)
    count = Column(Integer)

    order = relationship("OrderWithAllInfo", back_populates="products")
    product = relationship("ProductWithOrders", back_populates="orders")


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
    width = Column(Numeric(10, 2))
    price = Column(Numeric(10, 2))
    base_unit = Column(Integer, ForeignKey("units.id"))


class ClothStorage(Base):
    __tablename__ = "cloth_storage"

    number = Column(Integer, primary_key=True)
    article = Column(Integer, ForeignKey("clothes.article"))
    length = Column(Float)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    article = Column(Integer)

    # parent = Column(Integer, ForeignKey("products.id"), nullable=True)
    next_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    current_active = Column(Boolean, default=True)
    name = Column(String)
    width = Column(Integer)
    length = Column(Integer)
    image = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    changed_date = Column(DateTime, nullable=True)
    price = Column(Numeric(10, 2))
    size = Column(Integer, primary_key=True, nullable=False)


class ProductWithPrevious(Product):
    previous = relationship("ProductWithPrevious", uselist=False)


class ProductWithPreviousAccessoryCloth(Product):
    previous = relationship("ProductWithPreviousAccessoryCloth", uselist=False)
    accessories = relationship("Accessory", secondary=ProductAccessoryRelations)
    clothes = relationship("Cloth", secondary=ProductClothRelations)


class ProductWithOrders(Product):
    accessories = relationship("Accessory", secondary=ProductAccessoryRelations)
    clothes = relationship("Cloth", secondary=ProductClothRelations)
    orders = relationship(ProductOrderRelations, back_populates="product")


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

    article = Column(
        Integer,
        primary_key=True,
    )
    name = Column(String)
    type = Column(String)
    width = Column(Integer)
    length = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    image = Column(String, nullable=True)
    price = Column(Numeric(10, 2))
    kg_acceptable = Column(Boolean, default=False)


class AccessoriesStorage(Base):
    __tablename__ = "accessories_storage"

    article = Column(Integer, ForeignKey("accessories.article"), primary_key=True)
    amount = Column(Integer)


class AccessoriesStorageWithAccessory(AccessoriesStorage):
    accessory = relationship(Accessory)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    creation_date = Column(DateTime, server_default=func.now())
    completion_date = Column(DateTime, nullable=True)
    stage = Column(Enum(OrderStage))
    customer_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)


class OrderWithUsers(Order):
    customer = relationship(User, foreign_keys=[Order.customer_id])
    manager = relationship(User, foreign_keys=[Order.manager_id])


class OrderWithAllInfo(OrderWithUsers):
    products = relationship(ProductOrderRelations, back_populates="order")


class ManagerWithOrders(User):
    orders = relationship(Order, foreign_keys=[Order.manager_id], viewonly=True)


class ProductStorage(Base):
    __tablename__ = "products_storage"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    count = Column(Integer)


class AccessoryChanges(Base):
    __tablename__ = "accessory_history"

    id = Column(Integer, primary_key=True)
    accessory_article = Column(Integer, ForeignKey("accessories.article"))
    is_income = Column(Boolean, default=True)
    timestamp = Column(DateTime, server_default=func.now())
    amount = Column(Integer)


class ClothChanges(Base):
    __tablename__ = "cloth_history"

    id = Column(Integer, primary_key=True)
    cloth_article = Column(Integer, ForeignKey("clothes.article"))
    is_income = Column(Boolean, default=True)
    number = Column(Integer)
    length = Column(Numeric(10, 2))
    timestamp = Column(DateTime, server_default=func.now())


class Patch(Base):
    __tablename__ = 'patches'

    id = Column(Integer, primary_key=True)
    article = Column(Integer, ForeignKey('clothes.article'))
    width = Column(Numeric(10, 2))
    length = Column(Numeric(10, 2))
