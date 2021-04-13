from abc import ABC, abstractmethod


class DmicCommand(ABC):
    """Abstract class for Dmic commands."""

    def __init__(self, process_manager, command_pool):
        """Constructor for abstract class DmicCommand."""

        self._pm_receiver = process_manager
        self._c_pool = command_pool

    @abstractmethod
    def execute(self, data):
        """The commands action when executed."""
        pass


# Concrete Commands:


class C_Test(DmicCommand):
    def execute(self, data):
        print(f"""[TEST COMMAND]: Execute:
         |- data: {data}
         |- command pool: {self._c_pool}
         |- process manager: {self._pm_receiver}""")
