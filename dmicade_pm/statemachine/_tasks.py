from enum import Enum, auto


class DmicTaskType(Enum):
    TEST = auto()
    CHANGE_STATE = auto()


class DmicTask:
    def __init__(self, dmic_type: DmicTaskType, data):
        self.task_type = dmic_type
        self.data = data
