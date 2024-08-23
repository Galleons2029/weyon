from common import AbsException


class InvalidKBIdException(AbsException):
    def __init__(self, kb_id):
        self.kb_id = kb_id
        super().__init__(msg=f"Invalid Knowledge Id [{kb_id}]")
