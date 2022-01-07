from ..main import app
from fastapi import Request
from fastapi.responses import JSONResponse

class UsernameAlreadyExists(Exception):
    pass


@app.exception_handler(UsernameAlreadyExists)
async def username_already_exists(request: Request, ex: UsernameAlreadyExists):
    return JSONResponse(status_code=409,
                        content={
                            "description": "Username already exists"
                        })
