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

    def execute(self, data):
        logging.debug(f'[COMMAND: StartGame] Execute: {data=}')
        app_id = data
        is_running = False

        if not self._pm.verify_closed(app_id):
            logging.debug('[COMMAND: StartGame] game already running... closing game...')
            self._pm.close_app(app_id)

        for retry in range(self.START_TRIES):
            logging.debug(f'[COMMAND: StartGame] {retry=}')

            self._pm.start_app(app_id)
            is_running = self._pm.verify_running(app_id)

            if not is_running:
                logging.debug('[COMMAND: StartGame] not initialy verified as running...')
                time.sleep(1)
                is_running = self._pm.verify_running(app_id)

            logging.debug(f'[COMMAND: StartGame] {is_running=}')

            if is_running:
                break

        return is_running


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
