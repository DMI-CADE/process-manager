from abc import ABC

STATE_PREFIX = 'S_'


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


class DmicStatePool:

    def __init__(self, command_pool):
        """Constructor for class DmicStatePool

        Fills it the pool with a single instance of every subclass of
        DmicState from this module. The dictionary key for a state is
        the states class name without the global state prefix in
        lowercase.
        """

        self._pool = dict()

        # Fill pool with states.
        for key in globals():
            # Skip non classes and state interface.
            if not isinstance(globals()[key], type) or globals()[key] == DmicState:
                continue

            if issubclass(globals()[key], DmicState):
                state_id = key
                if state_id.startswith(STATE_PREFIX):
                    # Cut prefix off.
                    state_id = state_id[len(STATE_PREFIX):]

                state_id = state_id.lower()

                # Add instance of state to pool.
                self._pool[state_id] = globals()[key](command_pool)

    def get_state(self, state_type) -> DmicState:
        return self._pool.get(state_type)


class S_Test(DmicState):

    def enter(self):
        print('[DMICSTATE TEST]: Enter')

    def handle(self, task: dict):
        print('[DMICSTATE TEST]: Handle:', task)

    def exit(self):
        print('[DMICSTATE TEST]: Exit')


class S_Start(DmicState):
    pass
