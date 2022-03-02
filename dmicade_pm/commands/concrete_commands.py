import time
import logging

from abc import ABC, abstractmethod
from ..tasks import DmicTask, DmicTaskType


class DmicCommand(ABC):
    """Abstract class for Dmic commands."""

    def __init__(self, process_manager, command_pool):
        """Constructor for abstract class DmicCommand."""

        self._pm = process_manager
        self._c_pool = command_pool

    @abstractmethod
    def execute(self, data):
        """The commands action when executed."""
        pass


# Concrete Commands:


class C_Test(DmicCommand):
    def execute(self, data):
        print(f"""[COMMAND: TEST] Execute:
         |- data: {data}
         |- command pool: {self._c_pool}
         |- process manager: {self._pm}""")


class C_ChangeState(DmicCommand):
    def execute(self, data):
        state = data
        change_state_task = DmicTask(DmicTaskType.CHANGE_STATE, state)
        self._pm.queue_state_task(change_state_task)


class C_StartGame(DmicCommand):
    START_TRIES = 3
    RETRY_START_APP_DELAY = 1
    RETRY_VERIFIY_DELAY = 2 # Not lower then 2 for Godot games to be started-verified...

    def execute(self, data):
        logging.debug(f'[COMMAND: StartGame] Execute: {data=}')
        app_id = data
        is_running = False

        if not self._pm.verify_closed(app_id):
            logging.debug('[COMMAND: StartGame] Game already running... Closing game...')
            self._pm.close_app(app_id)

        for retry in range(self.START_TRIES):
            logging.debug(f'[COMMAND: StartGame] {retry=}')

            self._pm.close_app(app_id)

            self._pm.start_app(app_id)
            is_running = self._pm.verify_running(app_id)

            if not is_running:
                logging.debug(f'[COMMAND: StartGame] Verifiy: {is_running=}; Wait ({self.RETRY_VERIFIY_DELAY})s and retry verify...')
                time.sleep(self.RETRY_VERIFIY_DELAY)
                is_running = self._pm.verify_running(app_id)

            logging.debug(f'[COMMAND: StartGame] {is_running=}')

            if is_running:
                break

            time.sleep(self.RETRY_START_APP_DELAY)

        return is_running


class C_SetActiveApp(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: SetActiveApp] Execute: {data=}')
        self._pm.queue_state_task(DmicTask(DmicTaskType.SET_ACTIVE_APP, data))


class C_FocusApp(DmicCommand):
    FOCUS_REPS = 3
    FOCUS_REP_DELAY = 0.1

    def execute(self, data):
        logging.debug(f'[COMMAND: FocusApp] Execute: {data=}')
        self._pm.focus_app(data)
        app_is_focused = False

        for rep in range(self.FOCUS_REPS):
            app_is_focused = self._pm.verify_focus(data)
            if app_is_focused:
                break

            logging.debug(f'[COMMAND: FocusApp] app {data} not focused. Try: {rep+1}')
            time.sleep(self.FOCUS_REP_DELAY)

        return app_is_focused


class C_CloseGame(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: CloseGame] Execute: {data=}')
        app_id = data

        self._pm.close_app(app_id)

        is_closed = self._pm.verify_closed(app_id)
        return is_closed


class C_SendToUI(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: SendToUI] Execute: {data=}')
        bytes_sent = self._pm.send_to_ui(data)

        if bytes_sent:
            send_success = bytes_sent > 0
        else:
            send_success = False

        return send_success

class C_VerifyAppIsConfigured(DmicCommand):
    def execute(self, data):
        return data in self._pm.config_loader.configs

class C_SetInteractionFeedback(DmicCommand):
    def execute(self, data):
        self._pm.set_interaction_feedback(data)


class C_SetTimer(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: SetTimer] Execute: {data=}')
        self._pm.set_timer(data)


class C_SetTimerGame(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: SetTimerGame] Execute.')
        self._c_pool.invoke_command('settimer', int(self._pm.config_loader.global_config['game_timeout']))


class C_SetTimerMenu(DmicCommand):
    def execute(self, data):
        logging.debug(f'[COMMAND: SetTimerMenu] Execute.')
        self._c_pool.invoke_command('settimer', int(self._pm.config_loader.global_config['menu_timeout']))


class C_StopTimer(DmicCommand):
    def execute(self, data):
        self._pm.stop_timer()


class C_EnterSleep(DmicCommand):
    def execute(self, data):
        self._pm.enter_sleep()
