from abc import ABC
from ..helper import ObjectPool
from ._tasks import DmicTask, DmicTaskType
from ..commands import DmicCommandPool


class DmicState(ABC):
    """Abstract state class."""

    def __init__(self, command_pool: DmicCommandPool):
        self.command_pool = command_pool

    def enter(self) -> None:
        """Runs when entering the state."""
        pass

    def handle(self, task: DmicTask) -> None:
        """Handles occurring tasks.

        Args:
          task:
            A DmicTask to handle by the state.
        """
        pass

    def exit(self) -> None:
        """Runs when exiting the state."""
        pass


class DmicStatePool(ObjectPool):
    """Command pool for concrete"""

    STATE_PREFIX = 'S_'

    def __init__(self, command_pool: DmicCommandPool):
        """Constructor for class DmicStatePool."""
        super().__init__(globals(), DmicState, self.STATE_PREFIX, command_pool)


# Concrete States:


class S_Test(DmicState):

    def enter(self):
        print('[TEST STATE]: Enter')

    def handle(self, task: DmicTask):
        print('[TEST STATE]: Handle:', task)
        if task.task_type is DmicTaskType.TEST:
            self.command_pool.invoke_command('test', task.data)

    def exit(self):
        print('[TEST STATE]: Exit')


class S_Start(DmicState):
    pass
