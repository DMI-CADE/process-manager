import logging
import time

from abc import ABC
from ..helper import ObjectPool
from ..tasks import DmicTask, DmicTaskType
from ..commands import DmicCommandPool


UI_MSG = {
    'app_started': 'app_started:',
    'game_not_found': 'game_not_found',
    'app_closed': 'app_closed',
    'activate_menu': 'activate',
    'deactivate_menu': 'deactivate',
    'enter_idle': 'idle_enter',
    'exit_idle': 'idle_exit',
    'boot_menu': 'boot'
}


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
        logging.debug('[TEST STATE]: Enter')

    def handle(self, task: DmicTask):
        logging.debug(f'[TEST STATE]: Handle: {task=}')
        if task.type is DmicTaskType.TEST:
            self.command_pool.invoke_command('test', task.data)

    def exit(self):
        logging.debug('[TEST STATE]: Exit')


class S_Start(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_change_state = command_pool.get_object('changestate')
        self.cmd_send_to_ui = command_pool.get_object('sendtoui')

    def enter(self):
        logging.debug('[STATE: START] Enter.')
        self.cmd_send_to_ui.execute(UI_MSG['boot_menu'])
        self.cmd_change_state.execute('inmenu')


class S_InMenu(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_start_game = command_pool.get_object('startgame')
        self.cmd_change_state = command_pool.get_object('changestate')
        self.cmd_set_active_app = command_pool.get_object('setactiveapp')
        self.cmd_set_timer_menu = command_pool.get_object('settimermenu')
        self.cmd_send_to_ui = command_pool.get_object('sendtoui')

    def enter(self):
        logging.debug('[STATE: INMENU] Enter.')
        # TODO Focus menu
        self.cmd_set_timer_menu.execute(None)
        self.cmd_send_to_ui.execute(UI_MSG['activate_menu'])

    def handle(self, task):
        logging.debug(f'[STATE: INMENU] Handle: {task=}')

        if task.type is DmicTaskType.START_APP:
            logging.debug('[STATE: INMENU] Start game!')
            app_id = task.data

            # TODO check app id
            app_started = self.cmd_start_game.execute(app_id)
            self.cmd_send_to_ui.execute(UI_MSG['app_started'] + str(app_started).lower())

            if app_started:
                self.cmd_change_state.execute('ingame')
                self.cmd_set_active_app.execute(app_id)
                time.sleep(0.1)  # TODO focus game
                self.cmd_send_to_ui.execute(UI_MSG['deactivate_menu'])

            else:
                pass  # TODO handle game not starting

        elif task.type is DmicTaskType.TIMEOUT:
            self.cmd_change_state.execute('idle')

    def exit(self):
        logging.debug('[STATE: INMENU] Exit')


class S_Idle(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_change_state = command_pool.get_object('changestate')
        self.cmd_stop_timer = command_pool.get_object('stoptimer')
        self.cmd_set_interaction_feedback = command_pool.get_object('setinteractionfeedback')
        self.cmd_send_to_ui = command_pool.get_object('sendtoui')

    def enter(self):
        self.cmd_set_interaction_feedback.execute(True)
        self.cmd_stop_timer.execute(None)
        self.cmd_send_to_ui.execute(UI_MSG['enter_idle'])

    def handle(self, task):
        if task.type is DmicTaskType.INTERACTION:
            self.cmd_change_state.execute('inmenu')

    def exit(self):
        self.cmd_set_interaction_feedback.execute(False)
        self.cmd_send_to_ui.execute(UI_MSG['exit_idle'])


class S_InGame(DmicState):
    def __init__(self, command_pool):
        super().__init__(command_pool)
        self.cmd_close_game = command_pool.get_object('closegame')
        self.cmd_change_state = command_pool.get_object('changestate')
        self.cmd_set_timer_game = command_pool.get_object('settimergame')
        self.cmd_set_active_app = command_pool.get_object('setactiveapp')

    def enter(self):
        self.cmd_set_timer_game.execute(None)

    def handle(self, task):
        logging.debug(f'[STATE: INGAME] Handle: {task=}')
        if task.type is DmicTaskType.CLOSE_APP or \
                task.type is DmicTaskType.TIMEOUT:
            app_id = task.data
            self.cmd_close_game.execute(app_id)
            self.cmd_change_state.execute('inmenu')

        elif task.type is DmicTaskType.APP_CRASHED:
            logging.warning(f'[STATE: INGAME] Game crashed {task.data=}\n')
            app_id = task.data
            self.cmd_close_game.execute(app_id)
            self.cmd_change_state.execute('inmenu')

    def exit(self):
        self.cmd_set_active_app.execute(None)
