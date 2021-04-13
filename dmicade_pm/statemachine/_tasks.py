from enum import Enum, auto


class DmicTaskType(Enum):
    TEST = auto()
    CHANGE_STATE = auto()


class DmicTask:
    """Wrapper class containing values that make a dmic task.

    Attributes:
        task_type: A DmicTaskType indicating the type of the task.
        data: The tasks data.
    """

    def __init__(self, dmic_type: DmicTaskType, data):
        self.task_type = dmic_type
        self.data = data
