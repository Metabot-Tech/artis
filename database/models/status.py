from enum import Enum, auto


class Status(Enum):
    CREATED = auto()
    ONGOING = auto()
    DONE = auto()
    CANCELLED = auto()  # TODO: Fix typo
    UNKNOWN = auto()
    ERROR = auto()
    MISS = auto()
