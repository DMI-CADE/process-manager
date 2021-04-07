from abc import ABC, abstractmethod


class DmicCommand(ABC):
    """Abstract class for Dmic commands."""

    def __init__(self, project_manager, command_pool):
        self._pm_receiver = project_manager
        self._c_pool = command_pool

    @abstractmethod
    def execute(self, data):
        pass
