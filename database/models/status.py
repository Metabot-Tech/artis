from enum import Enum, auto


class Status(Enum):
    CREATED = auto()
    ONGOING = auto()
    DONE = auto()
    CANCELLED = auto()
    ERROR = auto()
