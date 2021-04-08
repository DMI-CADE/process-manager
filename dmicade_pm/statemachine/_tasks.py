from enum import Enum, auto


class DmicTaskType(Enum):
    TEST = auto()
    CHANGE_STATE = auto()
