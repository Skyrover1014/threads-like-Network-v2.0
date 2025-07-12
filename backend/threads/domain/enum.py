from enum import Enum

class ContentTypeEnum(str, Enum):
    POST = 'post'
    COMMENT = 'comment'

    @classmethod
    def choices(cls):
        return [(e.value, e.name.lower()) for e in cls]