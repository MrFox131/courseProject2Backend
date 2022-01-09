import hashlib
import os
from datetime import timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from . import exceptions, schemas
from .main import app, manager
from .db import models, get_db


def hash_password(password: str, salt: bytes = os.urandom(32)) -> (bytes, bytes):
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 10000)
    return key, salt


def verify_password(plain_password: str, password_salt: bytes, password_hash: bytes):
    return password_hash == hash_password(plain_password, password_salt)[0]


@manager.user_loader
async def get_user(identifier: str):
    db: Session = next(get_db())
    return db.query(models.User).filter(models.User.login == identifier).one_or_none()


@app.post(
    "/api/v1/register",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {"description": "Successfully created new user"}
                }
            },
        },
        409: {
            "description": "Nickname already exists",
            "content": {
                "application/json": {
                    "example": {"description": "Username already exists"}
                }
            },
        },
    },
    tags=["auth"],
)
async def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    same_login_person: models.User = await get_user(data.login)
    if same_login_person is not None:
        raise exceptions.UsernameAlreadyExists

    key, salt = hash_password(data.password)
    try:
        models.UserType(data.role)
    except:
        return JSONResponse(status_code=400, content={"description": "No such role"})
    new_user_model = models.User()
    new_user_model.login = data.login
    new_user_model.password = key
    new_user_model.name = data.name
    new_user_model.salt = salt
    new_user_model.role = models.UserType(data.role)

    try:
        db.add(new_user_model)
        db.commit()
        db.flush()
    except SQLAlchemyError as ex:
        print("SQLAlchemyError: ")
        print(ex)

        return JSONResponse(status_code=500, content={"description": "Database error"})

    return JSONResponse(
        status_code=200, content={"description": "Successfully created new user"}
    )


# noinspection PyShadowingNames
@app.post(
    "/api/v1/login",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI\
6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                        "token_type": "Bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid username or password",
            "content": {
                "application/json": {
                    "example": {"description": "Invalid username or password"}
                }
            },
        },
    },
    tags=["auth"],
)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    user: models.User = await get_user(data.username)
    if user is None:
        raise exceptions.InvalidNicknameOrPassword
    if not verify_password(data.password, user.salt, user.password):
        raise exceptions.InvalidNicknameOrPassword

    access_token = manager.create_access_token(
        data=dict(sub=user.login), expires=timedelta(days=1)
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post(
    "/api/v1/plane_login",
    responses={
        200: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI\
6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                        "token_type": "Bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid username or password",
            "content": {
                "application/json": {
                    "example": {"description": "Invalid username or password"}
                }
            },
        },
    },
    tags=["auth"],
)
async def plain_login(data: schemas.PlainLoginRequest):
    user: models.User = await get_user(data.login)
    if user is None:
        raise exceptions.InvalidNicknameOrPassword
    if not verify_password(data.password, user.salt, user.password):
        raise exceptions.InvalidNicknameOrPassword

    access_token = manager.create_access_token(
        data=dict(sub=user.login), expires=timedelta(days=1)
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/api/v1/roles", tags=["auth"])
async def get_roles():
    return JSONResponse(
        status_code=200,
        content={
            models.UserType.manager.value: "Менеджер",
            models.UserType.chef.value: "Директор",
            models.UserType.customer.value: "Заказчик",
            models.UserType.former_employee.value: "Швея",
            models.UserType.storage_manager.value: "Кладовщик",
        },
    )


@app.get(
    "/api/v1/me",
    response_model=schemas.UserModel,
    responses={
        200: {
            "description": "profile info",
            "content": {
                "application/json": {
                    "example": {"login": "mrfox131", "name": "Max", "role": 5}
                }
            },
        }
    },
    tags=["auth"],
)
async def check_token_expiration(user: models.User = Depends(manager)):
    return user
