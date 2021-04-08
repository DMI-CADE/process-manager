from .concrete_commands import *
from ..helper import ObjectPool


class CommandPool(ObjectPool):
    """Command Pool for concrete dmic commands."""
    COMMAND_PREFIX = 'C_'

    def __init__(self, process_manager):
        super().__init__()
        self.fill_object_pool(globals(), DmicCommand, self.COMMAND_PREFIX, process_manager, self)
        print('[STATEM] Object pool:', self._pool)

    def invoke_command(self, command_id, data):
        if not self.object_exists(command_id):
            raise Exception(f'[DMIC COMMAND POOL] Tried to invoke non existing command: {command_id}')
        self._pool[command_id].execute(data)
