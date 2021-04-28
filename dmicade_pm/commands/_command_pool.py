import logging

from .concrete_commands import *
from ..helper import ObjectPool


class DmicCommandPool(ObjectPool):
    """Command Pool for concrete dmic commands."""

    COMMAND_PREFIX = 'C_'

    def __init__(self, process_manager):
        super().__init__(globals(), DmicCommand, self.COMMAND_PREFIX, process_manager, self)
        logging.debug(f'[COMMAND POOL] {self._pool=})')

    def invoke_command(self, command_id, data):
        """Invokes a command in the command pool.

        Args:
          command_id:
            Command id of the command to invoke.
          data:
            Data passed to the command when invoked.
        """

        if not self.object_exists(command_id):
            raise Exception(f'[DMIC COMMAND POOL] Tried to invoke non existing command: {command_id}')
        self._pool[command_id].execute(data)
