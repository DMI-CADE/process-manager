from ._states import DmicStatePool


class DmicStateMachine:
    """Statemachine of the processmanager."""

    def __init__(self, command_pool):
        self._state_pool = DmicStatePool(command_pool)
        self._current_state = self._state_pool.get_state('start')
