import hashlib
import os

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .main import app, manager

from .db import models, get_db
from fastapi import Depends
from fastapi.responses import JSONResponse
from . import exceptions


def hash_password(password: str, salt: bytes = os.urandom(32)) -> (bytes, bytes):
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 10000)
    return key, salt


def verify_password(plain_password: str, password_salt: bytes, password_hash: bytes):
    return password_hash == hash_password(plain_password, password_salt)[0]


@manager.user_loader
async def get_user(identifier: str):
    db: Session = next(get_db())
    return db.query(models.User).filter(models.User.login == identifier).one_or_none()


@app.post("/api/v1/register", responses={
    200: {
        "description": "OK",
        "content": {
            "application/json": {
                "example": {"description": "Successfully created new user"}
            }
        }
    },
    409: {
        "description": "Nickname already exists",
        "content": {
            "application/json": {
                "example": {"description": "Username already exists"}
            }
        },
    }
}, tags=["auth"])
def register(login: str, password: str, name: str, role: int, db: Session = Depends(get_db)):
    same_login_person = get_user(login)
    if same_login_person is not None:
        raise exceptions.UsernameAlreadyExists

    key, salt = hash_password(password)
    new_user_model = models.User()
    new_user_model.login = login
    new_user_model.password = key
    new_user_model.name = name
    new_user_model.salt = salt
    new_user_model.role = models.UserType(role)
    try:
        db.add(new_user_model)
        db.commit()
        db.flush()
    except SQLAlchemyError as ex:
        print("SQLAlchemyError: ")
        print(ex)

        return JSONResponse(status_code=500, content={
            "description": "Database error"
        })

    return JSONResponse(
        status_code=200,
        content={
            "description": "Successfully created new user"
        }
    )
