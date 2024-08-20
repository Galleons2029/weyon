from common import AbsException


class EmbeddingException(AbsException):
    def __init__(self, model_uid):
        self.model_uid = model_uid


class EmbeddingNotFoundException(EmbeddingException):
    def __init__(self, model_uid):
        super().__init__(model_uid)
        self.msg = f"Embedding model-[{model_uid}] was not found,please check the model name"


class EmbeddingExistException(EmbeddingException):
    def __init__(self, model_uid):
        super().__init__(model_uid)
        self.msg = f"There has been a Embedding Model named {model_uid},if you want overwrite you can use `overwrite=True`"
