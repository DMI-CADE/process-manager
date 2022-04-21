import logging

from abc import ABC
from ..helper import ObjectPool
from ..tasks import DmicTask, DmicTaskType
from ..commands import *


UI_MSG = {
    'app_started': 'app_started:',
    'app_not_found': 'app_not_found',
    'app_closed': 'app_closed',
    'app_crashed': 'app_crashed',
    'activate_menu': 'activate',
    'deactivate_menu': 'deactivate',
    'enter_idle': 'idle_enter',
    'exit_idle': 'idle_exit',
    'boot_menu': 'boot'
}


class DmicState(ABC):
    """Abstract state class."""

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

    def __init__(self):
        """Constructor for class DmicStatePool."""
        super().__init__(globals(), DmicState, self.STATE_PREFIX)

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
    def enter(self):
        logging.debug('[STATE: START] Enter.')
        c_send_to_ui(UI_MSG['boot_menu'])
        c_set_volume('min')
        c_change_state('inmenu')


class S_InMenu(DmicState):
    def enter(self):
        logging.debug('[STATE: INMENU] Enter.')
        # TODO Focus menu
        c_set_timer_menu()
        c_send_to_ui(UI_MSG['activate_menu'])
        c_queue_menu_button_led_state(False)
        c_set_menu_button_colors()

    def handle(self, task):
        logging.debug(f'[STATE: INMENU] Handle: {task=}')

        if task.type is DmicTaskType.START_APP:
            logging.debug('[STATE: INMENU] Start game!')
            app_id = task.data

            # Verify app is configured
            if not c_verify_app_is_configured(app_id):
                logging.warning(f'[STATE: INMENU] Could not start app "{app_id}": not configured...')
                c_send_to_ui(UI_MSG['app_not_found'])
                return

            c_clear_button_colors()

            # Start app
            app_started = c_start_game(app_id)
            c_send_to_ui(UI_MSG['app_started'] + str(app_started).lower())

            if app_started:
                c_change_state('ingame')
                c_set_active_app(app_id)
                app_focused = c_focus_app(app_id)
                if not app_focused:
                    logging.warning(f'[STATE: INMENU] Could not focus app: {app_id}')
                    # TODO handle app not focused

                c_queue_menu_button_led_state(True)
                c_set_app_button_colors(app_id)

                c_send_to_ui(UI_MSG['deactivate_menu'])

            else:
                logging.warning(f'[STATE: INMENU] Could not start app: {app_id}')
                c_set_menu_button_colors()
                # TODO handle game not starting

        elif task.type is DmicTaskType.TIMEOUT:
            c_change_state('idle')

        elif task.type is DmicTaskType.CLOSE_APP:
            os.sync()
            logging.debug('[STATE: INMENU] \033[1m --- OS Synched! Ready for shutdown... --- \033[0m')

    def exit(self):
        logging.debug('[STATE: INMENU] Exit')


class S_Idle(DmicState):
    def enter(self):
        self.waiting_for_interaction = True
        c_set_interaction_feedback(True)
        c_stop_timer()
        c_send_to_ui(UI_MSG['enter_idle'])
        c_queue_menu_button_led_state(True)
        c_clear_button_colors()
        time.sleep(1)
        c_change_button_colors({"RAINBOW": True})

    def handle(self, task):
        if task.type is DmicTaskType.INTERACTION or task.type is DmicTaskType.CLOSE_APP:
            if not self.waiting_for_interaction:
                return

            self.waiting_for_interaction = False

            c_change_state('inmenu')
            c_set_interaction_feedback(False)
            c_send_to_ui(UI_MSG['exit_idle'])

        if task.type is DmicTaskType.SLEEP:
            c_change_state('sleep')

    def exit(self):
        c_set_interaction_feedback(False)


class S_InGame(DmicState):
    def enter(self):
        c_set_timer_game()

    def handle(self, task):
        logging.debug(f'[STATE: INGAME] Handle: {task=}')
        if task.type is DmicTaskType.CLOSE_APP or \
                task.type is DmicTaskType.TIMEOUT:
            self._go_to_menu(task, 'app_closed')

        elif task.type is DmicTaskType.APP_CRASHED:
            logging.warning(f'[STATE: INGAME] Game crashed {task.data=}\n')
            self._go_to_menu(task, 'app_crashed')

    def _go_to_menu(self, task, msg_id):
        app_id = task.data
        c_close_game(app_id)
        c_send_to_ui(UI_MSG[msg_id])
        c_change_state('inmenu')

    def exit(self):
        c_set_active_app(None)

class S_Sleep(DmicState):
    def enter(self):
        c_queue_menu_button_led_state(False)
        c_clear_button_colors()
        c_enter_sleep()

    def handle(self, task):
        logging.debug(f'[STATE: SLEEP] Handle: {task=}')
        if task.type is DmicTaskType.WAKE:
            c_change_state('inmenu')

    def exit(self):
        c_send_to_ui(UI_MSG['exit_idle'])
