"""公共模块，包含统一相应格式"""
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AbsException(Exception):
    """抽象异常，主要是负责业务上的异常，也就是开发者手动添加的异常，方便全局异常处理机制"""
    def __init__(self, msg=None):
        super().__init__()
        self.msg = msg or ""


class ResponseCode(Enum):
    """统一响应体中的状态码"""
    SUCCESS = 200
    FAILED = 400
    ERROR = 500


class BaseResponse(BaseModel):
    """统一响应体"""
    code: ResponseCode = Field(description="返回状态码")
    msg: str = Field(description="返回消息", default="")
    data: Any = Field(description="返回数据", default=None)

    def __getstate__(self):
        return vars(self)


def success(msg=ResponseCode.SUCCESS.name, data=None):
    """返回成功的响应体"""
    return BaseResponse(code=ResponseCode.SUCCESS, msg=msg, data=data)


def failed(code=ResponseCode.FAILED, msg=ResponseCode.FAILED.name, data=None):
    """返回失败的响应体"""
    return BaseResponse(code=code, msg=msg, data=data)


def error(code=ResponseCode.ERROR, msg=ResponseCode.ERROR.name):
    """返回错误响应体，这里的错误一般值系统内部出现了非业务上的异常，比如外部HTTP无法访问等"""
    return BaseResponse(code=code, msg=msg)
