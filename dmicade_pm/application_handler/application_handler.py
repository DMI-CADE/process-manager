import json
import subprocess

from .applications import DmicAppNotRunningException, DmicAppNotConfiguredException, dmic_app_process_factory


class DmicApplicationHandler:
    """Window Handler for dmicade process manager.

    Houses functions for starting applications, controlling focus,
    closing them and verifying the applications state.

    Attributes:
      apps_config : dict
        Application configurations loaded from the config file.
      apps_location : str
        Path to where the application folders are located. Uses default
        when '_apps_location' not set in config file.
      running_apps : dict
        Currently running DmicApp instances with their app id as keys.
    """

    """Default apps config file path."""
    APPS_CONFIG_FILE_PATH = './dmicade_pm/application_handler/apps_config.json'
    CMD_GET_FOCUSED_WINDOW_ID = 'xdotool getactivewindow'
    CMD_SEARCH_WINDOW = 'xdotool search --onlyvisible %s | head -n1'  # Only returns first found id.
    CMD_FOCUS_WINDOW_SYNC = 'xdotool search --onlyvisible %s windowactivate --sync'
    CMD_KILL_WINDOW = 'xdotool search --onlyvisible %s windowkill'

    def __init__(self, apps_location=''):
        """Constructor for class DmicApplicationHandler"""

        self.apps_config = dict()
        with open(self.APPS_CONFIG_FILE_PATH) as json_file:
            self.apps_config = json.load(json_file)

        self.apps_location = apps_location
        if not apps_location:
            self.apps_location = self.apps_config['_apps_location']

        self.running_apps = dict()

    def start_app(self, app_id):
        """Starts an app by its id.

        Stops any app with same id that is currently running prior.
        Adds corresponding crash event function to the apps crash
        event.

        Args:
          app_id: str
            The app to start.

        Raises:
          DmicAppNotConfiguredException: If app is not configured correctly.
        """

        # print('[APP HANDLER] Start app:', app_id)
        # print('[APP HANDLER] current apps:', self.running_apps)
        app_config = self._get_app_config(app_id)

        # Stop/Remove if already present
        if app_id in self.running_apps:
            self.running_apps[app_id].stop()

        app_process = dmic_app_process_factory(app_id, app_config)
        app_process.run(self.apps_config['_apps_location'])
        app_process.crash_event += self._get_crash_callback_function(app_id)

        self.running_apps[app_id] = app_process
        # print('[APP HANDLER] current apps:', self.running_apps)

    def verify_running(self, app_id):
        """Checks if a application is running"""

        app_exists = app_id in self.running_apps
        # print('[APP HANDLER] Verify running: app_exists:', app_exists)
        app_process_is_running = False
        window_found = False
        if app_exists:
            app_process_is_running = self.running_apps[app_id].is_running()
            # print('[APP HANDLER] Verify running: app_process_is_running:', app_process_is_running)
            try:
                window_found = self._get_window_id(app_id) > 0
                # print('[APP HANDLER] Verify running: window_found:', window_found)
            except DmicAppNotRunningException:
                window_found = False

        return app_exists and app_process_is_running and window_found

    def focus_app_sync(self, app_id):
        """Focuses application synchronously."""

        try:
            window_term = self.running_apps[app_id].get_window_search_term()
            sp_check_output(self.CMD_FOCUS_WINDOW_SYNC % window_term)
        except subprocess.CalledProcessError as e:
            print('[APP HANDLER] focus app subprocess error:', e)
            return False

        return True

    def verify_focus(self, app_id):
        """Checks if application is focused."""

        try:
            focused_window_id = int(sp_check_output(self.CMD_GET_FOCUSED_WINDOW_ID))
            # print('[APP HANDLER] focused_window_id:', focused_window_id)
            app_window_id = self._get_window_id(app_id)
            # print('[APP HANDLER] app_window_id:', app_window_id)
        except DmicAppNotRunningException:
            return False

        return focused_window_id == app_window_id

    def close_app(self, app_id):
        """Closes an application."""

        # print(f'[APP HANDLER] Close: {app_id}...')
        window_search_term = dmic_app_process_factory(app_id, self._get_app_config(app_id)).get_window_search_term()
        try:
            # print(f'[APP HANDLER] Windowkill: {window_search_term}...')
            sp_check_output(self.CMD_KILL_WINDOW % window_search_term)
        except subprocess.CalledProcessError as e:
            print('[APP HANDLER] close app subprocess error:', e)

        if app_id in self.running_apps:
            self.running_apps[app_id].stop()
            del self.running_apps[app_id]

    def verify_closed(self, app_id):
        """Checks if an application is closed."""

        window_search_term = dmic_app_process_factory(app_id, self._get_app_config(app_id)).get_window_search_term()
        found_window = sp_check_output(self.CMD_SEARCH_WINDOW % window_search_term)
        return len(found_window) == 0

    def _get_app_config(self, app_id):
        """Gets the applications config."""

        if app_id not in self.apps_config:
            raise DmicAppNotConfiguredException(app_id)

        return self.apps_config[app_id]

    def _get_window_id(self, app_id):
        """Gets the window id of an application."""

        try:
            window_term = self.running_apps[app_id].get_window_search_term()
            window_id = sp_check_output(self.CMD_SEARCH_WINDOW % window_term)
            window_id = int(window_id)
        except ValueError:
            raise DmicAppNotRunningException(app_id)
        except KeyError:
            raise DmicAppNotRunningException(app_id)

        return window_id

    def _get_crash_callback_function(self, app_id):
        return lambda x: print(f'[CRASH EVENT SUB] crashed event invoked... {app_id}')


def sp_check_output(cmd):
    return subprocess.check_output(cmd, shell=True)
