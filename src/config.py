import os


class BaseConfig(type):
    """这个配置类的元类使得配置能够和环境变量结合，这样便于docker等容器化部署时进行单项配置"""

    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if key in os.environ and not callable(value):
                attrs[key] = os.environ[key]
        return type.__new__(cls, name, bases, attrs)


class UploadConfig(metaclass=BaseConfig):
    # 上传文件保存路径
    UPLOAD_SAVING_PATH: str = "upload"
    #
    MAX_FILE_SIZE: int = 100
    # 允许的 MIME 类型
    ALLOWED_MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ["docx"]
    }
