from enum import Enum, auto


class DmicTaskType(Enum):
    TEST = auto()
    INTERACTION = auto()
    CHANGE_STATE = auto()  # Handled by state machine.
    START_APP = auto()
    CLOSE_APP = auto()
    SET_ACTIVE_APP = auto()  # Handled by state machine.
    APP_CRASHED = auto()
    TIMEOUT = auto()


class DmicTask:
    """Wrapper class containing values that make a dmic task.

    Attributes:
        dmic_task_type: A DmicTaskType indicating the type of the task.
        data: The tasks data.
    """

    def __init__(self, dmic_task_type: DmicTaskType, data):
        self.type = dmic_task_type
        self.data = data
