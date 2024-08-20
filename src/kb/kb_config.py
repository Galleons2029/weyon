from typing import Union

from config import BaseConfig


class UploadConfig(metaclass=BaseConfig):
    """文件上传配置"""

    UPLOAD_SAVING_PATH: str = "upload"
    """上传文件保存路径"""

    MAX_FILE_SIZE: int = 100
    """文件最大限制（MB）"""

    ALLOWED_MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ["docx"]
    }
    """允许的 MIME 类型"""


class QdrantConfig(metaclass=BaseConfig):
    """Qdrant配置"""

    LOCATION: str = "http://192.168.100.111:6333"
    """Qdrant 连接地址"""


class XinferenceConfig(metaclass=BaseConfig):
    API_KEY: str = "dummy"
    """Xinference API 接口密钥"""
    BASE_URL: str = "http://192.168.100.111:9997/v1"
    """Xinference接口url"""
    EMBEDDINGS: Union[str, list[str]] = "bge-m3"


class DocxImageParserConfig(metaclass=BaseConfig):
    IMG_SAVE_PATH: str = "./img"
    IMG_PREFIX: str = "../img/"
