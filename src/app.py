import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import config
from common import failed, AbsException
from kb import kb_router

config.logs_config()
app = FastAPI(title='WeYon AI Open Platform', version='0.1.0')

app.include_router(kb_router.router)


@app.exception_handler(AbsException)
async def file_exception(request: Request, exc: AbsException):
    content = jsonable_encoder(failed(msg=exc.msg))
    logging.debug(f"File Exception {exc.msg}", exc_info=exc)
    return JSONResponse(status_code=400, content=content)


@app.get("/")
async def root():
    return {"message": "Hello World"}
