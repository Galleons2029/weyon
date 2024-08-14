from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResponseCode(Enum):
    SUCCESS = 200
    FAILED = 400
    ERROR = 500


class BaseResponse(BaseModel):
    code: ResponseCode = Field(description="返回状态码")
    msg: str = Field(description="返回消息", default="")
    data: Any = Field(description="返回数据", default=None)

    @staticmethod
    def success(msg=ResponseCode.SUCCESS.name, data=None):
        return BaseResponse(code=ResponseCode.SUCCESS, msg=msg, data=data)

    @staticmethod
    def failed(code=ResponseCode.FAILED, msg=ResponseCode.FAILED.name, data=None):
        return BaseResponse(code=code, msg=msg, data=data)

    @staticmethod
    def error(code=ResponseCode.ERROR, msg=ResponseCode.ERROR.name):
        return BaseResponse(code=code, msg=msg)
