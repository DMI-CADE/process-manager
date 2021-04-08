from .concrete_commands import *



class CommandPool:
    """Command Pool for concrete dmic commands"""
    COMMAND_PREFIX = 'C_'

    def __init__(self):
        self._pool = dict()

        for key in globals():
            print(key)