import subprocess
import threading
import logging

from abc import ABC, abstractmethod
from ..helper import DmicEvent, DmicException


class DmicApp(ABC):
    """Abstract class DmicApp for all Dmic-Application types."""

    EXE = 'executable'
    MAME_ROM = 'mame_rom'

    def __init__(self, app_id, app_config):
        self.app_id = app_id
        self.app_config = app_config
        self.crash_event = DmicEvent()
        self.sub_process = None

        self._crash_check_thread = None
        self._should_be_running = False

    def run(self, apps_path):
        """Starts the app.

        Starts the app by executing the _start_app function of the
        child.
        Starts a thread wich checks for crashes.

        Args:
          apps_path: string
            Main media directory.
        """

        logging.debug('[DMICAPP] Run...')
        self.sub_process = self._start_app(apps_path)

        self._crash_check_thread = threading.Thread(
            target=self._wait_for_crash,
            daemon=True)
        self._crash_check_thread.name = self.app_id.title().replace('-', '').replace('_', '') + 'CrashCheckThread'
        self._crash_check_thread.start()

        self._should_be_running = True

    def _wait_for_crash(self):
        """Synchronously waits until the suporcess closes.

        Updates crash event when app is supposed to be running.
        """

        self.sub_process.wait()

        if self._should_be_running:
            logging.warning('[DMICAPP] APP CRASH!')
            self.crash_event.update()

    def stop(self):
        self._should_be_running = False

        logging.debug(f'[DMICAPP] Terminate: {self.app_id}')
        self.sub_process.terminate()

    def is_running(self):
        return self._should_be_running

    @abstractmethod
    def _start_app(self, apps_path) -> subprocess.Popen:
        """Starts the app in a subprocess.

        Returns:
          The supprocess the app is running in.
        """
        pass

    @abstractmethod
    def get_window_search_term(self) -> str:
        """Returns a string that can be used to identify the app window."""
        pass


class DmicAppMameRom(DmicApp):
    """Class for DmicApp type 'Mame Rom'."""

    def get_window_search_term(self):
        return 'MAME'

    def _start_app(self, apps_path):
        logging.debug('[DMICAPP MAME] Start...')
        if 'command' not in self.app_config:
            raise DmicAppNotConfiguredException(self.app_id)

        cmd = self.app_config['command']
        cmd = cmd.replace('%%path%%', apps_path)
        logging.debug(f'[DMICAPP MAME] Run: {cmd}')

        return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)


class DmicAppExecutable(DmicApp):
    """Calss for DmicApp type 'Executable'."""

    def get_window_search_term(self):
        if 'exe' not in self.app_config:
            raise DmicAppNotConfiguredException(self.app_id)

        return self.app_config['exe']

    def _start_app(self, apps_path):
        logging.debug('[DMICAPP EXE] Start...')
        if 'exe' not in self.app_config:
            raise DmicAppNotConfiguredException(self.app_id)

        cmd = f'{apps_path}{self.app_id}/{self.app_config["exe"]}'.split()
        # Use debug path if present.
        if '_debug_path' in self.app_config:
            cmd = self.app_config['_debug_path']

        return subprocess.Popen(cmd, stdout=subprocess.PIPE)


class DmicAppNotRunningException(DmicException):
    def __init__(self, app_id):
        self.app_id = app_id


class DmicAppNotConfiguredException(DmicException):
    def __init__(self, app_id):
        self.app_id = app_id


def dmic_app_process_factory(app_id, app_config) -> DmicApp:
    """Factory for Dmic-Applications."""

    try:
        if app_config['type'] == DmicApp.EXE:
            new_app_process = DmicAppExecutable(app_id, app_config)
        elif app_config['type'] == DmicApp.MAME_ROM:
            new_app_process = DmicAppMameRom(app_id, app_config)
        else:
            raise DmicAppNotConfiguredException(app_config)
    except ValueError:
        raise DmicAppNotConfiguredException(app_config)
    except KeyError:
        raise DmicAppNotConfiguredException(app_config)

    return new_app_process
