"""启动脚本，注意启动位置必须和app同一级目录，或者将该目录添加到PYTHONPATH中"""
import logging

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import config
from common import failed, AbsException
from config import file_handle
from kb import kb_router

# 这里的 ‘G’ 代表Global的意思
config.logs_config(handlers=file_handle(tag='G'))
app = FastAPI(title='WeYon AI Open Platform', version='0.1.0', root_path="/api/v1")

app.include_router(kb_router.router)

logger = logging.getLogger(__name__)
logger.addHandler(config.file_handle(tag="EXC"))
logger.setLevel(logging.DEBUG)


@app.exception_handler(AbsException)
async def file_exception(_, exc: AbsException):
    """业务全局异常处理"""
    content = jsonable_encoder(failed(msg=exc.msg))
    logger.debug("Exception %s", exc.msg, exc_info=exc)
    return JSONResponse(status_code=400, content=content)


@app.get("/", summary="链接测试使用")
async def root():
    """测试连接使用"""
    return {"message": "Hello World"}
