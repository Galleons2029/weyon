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
    """Xinference 链接配置"""
    API_KEY: str = "dummy"
    """Xinference API 接口密钥"""
    BASE_URL: str = "http://192.168.100.111:9997/v1"
    """Xinference接口url"""
    EMBEDDINGS: Union[str, list[str]] = "bge-m3"


class DocxImageParserConfig(metaclass=BaseConfig):
    """Docx 文档解析配置"""
    IMG_SAVE_PATH: str = "./img"
    """文档中图片的保存位置，相对启动目录"""
    IMG_PREFIX: str = "../img/"
    """用markdown图片代替文字时图片的前缀。
    主要是为了传递给前端的markdown能够正确请求到图片。
    这里需要注意相对|绝对路径的问题，正式环境建议使用一个图床服务或者OSS链接地址。
    """


class DocxMetadataConfig:
    """向量数据库中payload的结构"""
    METADATA = 'metadata'
    """元数据：字典"""
    PARENT_ID = 'parent'
    """父子查询时需要使用的父节点记录"""
    ORDER_BY = 'idx'
    """文档顺序，这个顺序的作用于只在同一个文档中有效。"""
    PAGE_CONTENT = 'page_content'
    """具体的知识文档数据，最关键的数据"""
    DOC_FILENAME = 'doc'
    """文档名称，在指定文档检索时使用，这个非唯一"""
    FILE_ID = 'file_id'
    """文档id，在指定文档检索时使用，唯一且与文件系统对应"""
