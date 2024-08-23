import logging
import os
from datetime import date
from typing import Literal, Any

import coloredlogs


class BaseConfig(type):
    """这个配置类的元类使得配置能够和环境变量结合，这样便于docker等容器化部署时进行单项配置"""

    def __new__(mcs, name, bases, attrs):
        """创建"""
        for key, value in attrs.items():
            if key in os.environ and not callable(value):
                attrs[key] = os.environ[key]
        return type.__new__(mcs, name, bases, attrs)


class LogConfig(metaclass=BaseConfig):
    """日志配置"""
    FIELD_STYLES: dict[str, dict[str, Any]] = {
        'asctime': {'color': 'green'},
        'name': {'color': 'blue'},
        'filename': {'color': 'magenta'},
        'pathname': {'color': 'magenta'},
        'lineno': {'color': 'yellow'},
        'levelname': {'color': 'cyan', 'bold': True},
        'processName': {'color': 'green', 'bold': True},
    }
    """Mapping of log format names to default font styles."""
    LEVEL_STYLES: dict[str, dict[str, Any]] = {
        'debug': {'color': 'blue'},
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'background': 'red', 'bold': True},
    }
    """Mapping of log level names to default font styles."""

    BASIC_FORMAT: str = '{asctime} - {module:^20} - {name:^20} - {filename}[line:{lineno}] - [{levelname}]: {message}'
    """基础日志格式"""
    LOG_STYLE: Literal["%", "{", "$"] = '{'

    COLORED_FORMAT: coloredlogs.ColoredFormatter = coloredlogs.ColoredFormatter(
        fmt=BASIC_FORMAT,
        style=LOG_STYLE,
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES
    )
    "带颜色的日志格式"
    LOG_ENCODING = 'utf-8'
    """日志文件的编码方式"""
    LOG_FILE_PATH = "./logs/"
    """日志文件输出目录"""


def console_handle():
    """控制台日志处理函数"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(LogConfig.COLORED_FORMAT)
    return console_handler


def file_handle(tag="L", filename=None, ext="log"):
    """文件日志记录"""
    os.makedirs(LogConfig.LOG_FILE_PATH, exist_ok=True)
    file_path = os.path.join(LogConfig.LOG_FILE_PATH, filename or f"{date.today()}_{tag}.{ext}")
    file_handler = logging.FileHandler(file_path, encoding=LogConfig.LOG_ENCODING)
    file_handler.setFormatter(logging.Formatter(LogConfig.BASIC_FORMAT, style=LogConfig.LOG_STYLE))
    return file_handler


def logs_config(logger: logging.Logger = None, filename=None):
    """日志初始化配置"""
    handlers = [console_handle()]
    if filename:
        handlers.append(file_handle(filename))
    if logger:
        logger.addHandler(*handlers)
    else:
        logging.basicConfig(level=logging.INFO,
                            format=LogConfig.BASIC_FORMAT,
                            style=LogConfig.LOG_STYLE,
                            handlers=handlers)
