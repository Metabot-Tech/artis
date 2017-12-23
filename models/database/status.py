from enum import Enum, auto


class Status(Enum):
    CREATED = auto()
    ONGOING = auto()
    DONE = auto()
    ERROR = auto()
