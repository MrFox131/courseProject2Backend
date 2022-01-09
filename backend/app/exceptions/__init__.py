from ..main import app
from fastapi import Request
from fastapi.responses import JSONResponse


class UsernameAlreadyExists(Exception):
    pass


class InvalidNicknameOrPassword(Exception):
    pass


class ArticleAlreadyExists(Exception):
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
