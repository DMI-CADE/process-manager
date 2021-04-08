from abc import ABC
from ..helper import ObjectPool


class DmicState(ABC):
    """Abstract state class."""

    def __init__(self, command_pool):
        self.command_pool = command_pool

    def enter(self) -> None:
        """Runs when entering the state."""
        pass

    def handle(self, task: dict) -> None:
        """Handles occurring tasks."""
        pass

    def exit(self) -> None:
        """Runs when exiting the state."""
        pass


class DmicStatePool(ObjectPool):
    """Command pool for concrete"""

    STATE_PREFIX = 'S_'

    def __init__(self, command_pool):
        """Constructor for class DmicStatePool."""
        super().__init__(globals(), DmicState, self.STATE_PREFIX, command_pool)


class S_Test(DmicState):

    def enter(self):
        print('[DMICSTATE TEST]: Enter')

    def handle(self, task: dict):
        print('[DMICSTATE TEST]: Handle:', task)

    def exit(self):
        print('[DMICSTATE TEST]: Exit')


class S_Start(DmicState):
    pass
