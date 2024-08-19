from abc import ABC


class FileException(Exception, ABC):
    """文件异常"""

    def __init__(self, filename, msg=None):
        self.filename = filename
        self.msg = msg or ""


class FileSizeException(FileException):
    """文件大小异常，一般是文件大小不符合预定的规则，一般是过大了"""

    def __init__(self, filename: str, msg=None):
        super().__init__(filename)
        self.msg = msg or f"The size of file-[{filename}] is out of limit"


class FileTypeException(FileException):
    """文件类型异常"""

    def __init__(self, filename, msg=None, mime_type=None):
        super().__init__(filename)
        self.mime_type = mime_type
        self.msg = msg or f"The type of file-[{filename}] is out of limit"
