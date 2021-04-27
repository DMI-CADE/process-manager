from abc import ABC
from ..helper import ObjectPool
from ..tasks import DmicTask, DmicTaskType
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
    """State pool for concrete DmicStates."""

    STATE_PREFIX = 'S_'

    def __init__(self, command_pool: DmicCommandPool):
        """Constructor for class DmicStatePool."""
        super().__init__(globals(), DmicState, self.STATE_PREFIX, command_pool)

        logging.debug(f'[STATE POOL]: {self._pool=}')


# Concrete States:


class S_Test(DmicState):

    def enter(self):
        print('[TEST STATE]: Enter')

    def handle(self, task: DmicTask):
        print('[TEST STATE]: Handle:', task)
        if task.type is DmicTaskType.TEST:
            self.command_pool.invoke_command('test', task.data)

    def exit(self):
        print('[TEST STATE]: Exit')


class S_Start(DmicState):
    pass


class S_InMenu(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_start_game = command_pool.get_object('startgame')
        self.cmd_change_state = command_pool.get_object('changestate')

    def enter(self):
        logging.debug('[STATE: INMENU] Enter.')

    def handle(self, task):
        logging.debug(f'[STATE: INMENU] Handle: {task=}')

        if task.type is DmicTaskType.START_APP:
            logging.debug('[STATE: INMENU] Start game!')
            app_id = task.data
            self.cmd_change_state.execute('ingame')
            self.cmd_start_game.execute(app_id)

    def exit(self):
        logging.debug('[STATE: INMENU] Exit')


class S_InGame(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_close_game = command_pool.get_object('closegame')
        self.cmd_change_state = command_pool.get_object('changestate')

    def handle(self, task):
        logging.debug(f'[STATE: INGAME] Handle: {task=}')
        if task.type is DmicTaskType.CLOSE_APP:
            app_id = task.data
            self.cmd_close_game.execute(app_id)
            self.cmd_change_state.execute('inmenu')

        if task.type is DmicTaskType.APP_CRASHED:
            logging.warning(f'\n [STATE: INGAME] Game crashed {task.data=}')
            app_id = task.data
            self.cmd_close_game.execute(app_id)
            self.cmd_change_state.execute('inmenu')
