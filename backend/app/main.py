import uvicorn
from fastapi import FastAPI
from fastapi_login import LoginManager

from .db import engine
from .db import models as models

app = FastAPI(redoc_url="/api/redoc")
models.Base.metadata.create_all(bind=engine)
SECRET = "5c4b93fc508656a184874da6dd27a8db74b1dcf8db2d489be4afbc36499b312737c1c7228b6a2e0469ac9645d24dbabdda3feb49e00c6\
f14b0bad7e4b1faab16debcab276930365faa28d2127bcc7bb974869fe371a9b6b2d082e97321fcc17a799d577a4c1856e29aa8783f3a3d2d25a0f2\
04493628c9f2a87bda24b7bbb5cd"
manager = LoginManager(SECRET, "/api/v1/login", use_cookie=True)


from . import auth

@app.get("/hello_world")
def hello_world():
    return "hello"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
