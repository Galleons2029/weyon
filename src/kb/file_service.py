import os.path
import uuid

import magic

from kb.file_excep import FileTypeException, FileSizeException
from kb.kb_config import UploadConfig

# 创建一个 magic.Magic 对象，使用 mime 真类来检测 MIME 类型
mime = magic.Magic(mime=True)


def check_file_type(byte, filename):
    """检查文件类型在指定类型范围内"""
    # 以确定 MIME 类型
    file_mime_type = mime.from_buffer(byte)

    # 检查 MIME 类型是否被允许
    if file_mime_type not in UploadConfig.ALLOWED_MIME_TYPES:
        raise FileTypeException(filename, msg="File MIME type not allowed")

    # 检查文件扩展名是否与 MIME 类型匹配
    file_extension = get_file_ext(filename)
    if not any(file_extension in extensions for extensions in UploadConfig.ALLOWED_MIME_TYPES.values()):
        raise FileTypeException(filename, msg="File extension does not match MIME type")


def check_file_size(byte):
    """检查文件大小不得超出指定大小"""
    limit_size = UploadConfig.MAX_FILE_SIZE * 1024 * 1024
    if len(byte) > limit_size:
        raise FileSizeException(filename="", msg=f"File size limited in {UploadConfig.MAX_FILE_SIZE}MB")


def get_file_ext(filename) -> str:
    return filename.split('.')[-1].lower()


def save_file(contents, filename) -> str:
    """
    保存文件到配置目录
    :param contents: 文件内容
    :param filename: 上传时的文件名
    :return: 文件id
    """
    file_id = uuid.uuid4().__str__()
    os.makedirs(UploadConfig.UPLOAD_SAVING_PATH, exist_ok=True)
    save_file_path = os.path.join(UploadConfig.UPLOAD_SAVING_PATH,
                                  file_id + '.' + get_file_ext(filename))
    with open(save_file_path, 'wb') as f:
        f.write(contents)
    return file_id
