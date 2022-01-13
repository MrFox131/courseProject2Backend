from ..main import app
from fastapi import Request
from fastapi.responses import JSONResponse


class UsernameAlreadyExists(Exception):
    pass


class InvalidNicknameOrPassword(Exception):
    pass


class ArticleAlreadyExists(Exception):
    pass


class InvalidClothStorage(Exception):
    pass


class InsufficientClothLength(Exception):
    pass


class InvalidAccessoryStorage(Exception):
    pass


class InsufficientAccessoryCount(Exception):
    pass


class ArticleDoesNotExist(Exception):
    pass


class OrderDoesNotExists(Exception):
    pass


class InsufficientPrivileges(Exception):
    pass


@app.exception_handler(UsernameAlreadyExists)
async def username_already_exists(request: Request, ex: UsernameAlreadyExists):
    return JSONResponse(
        status_code=409, content={"description": "Username already exists"}
    )


@app.exception_handler(InvalidNicknameOrPassword)
async def invalid_username_or_password(request: Request, ex: InvalidNicknameOrPassword):
    return JSONResponse(
        status_code=401, content={"description": "Invalid username or password"}
    )


@app.exception_handler(ArticleAlreadyExists)
async def article_already_exists(request: Request, ex: ArticleAlreadyExists):
    return JSONResponse(
        status_code=409, content={"description": "Article already exists"}
    )


@app.exception_handler(InvalidClothStorage)
async def invalid_cloth_storage(request: Request, ex: InvalidClothStorage):
    return JSONResponse(
        status_code=404, content={"description": "No such article or number"}
    )


@app.exception_handler(InsufficientClothLength)
async def insufficient_cloth_length(request: Request, ex: InsufficientClothLength):
    return JSONResponse(
        status_code=409, content={"description": "Insufficient cloth length"}
    )


@app.exception_handler(InvalidAccessoryStorage)
async def invalid_cloth_storage(request: Request, ex: InvalidAccessoryStorage):
    return JSONResponse(
        status_code=404, content={"description": "No such article or number"}
    )


@app.exception_handler(InsufficientAccessoryCount)
async def insufficient_cloth_length(request: Request, ex: InsufficientAccessoryCount):
    return JSONResponse(
        status_code=409, content={"description": "Insufficient accessory count"}
    )


@app.exception_handler(ArticleDoesNotExist)
async def article_does_not_exist(request: Request, ex: ArticleDoesNotExist):
    return JSONResponse(
        status_code=404, content={"description": "Article does not exist"}
    )


@app.exception_handler(OrderDoesNotExists)
async def order_does_not_exist(request: Request, ex: OrderDoesNotExists):
    return JSONResponse(
        status_code=404, content={"description": "Order does not exist"}
    )


@app.exception_handler(InsufficientPrivileges)
async def insufficient_privileges(request: Request, ex: InsufficientPrivileges):
    return JSONResponse(
        status_code=401, content={"description": "Insufficient privileges"}
    )
