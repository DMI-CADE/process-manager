from .tasks import DmicTask, DmicTaskType
from .application_handler import DmicApplicationHandler
from .timer import DmicTimer, SleepManager
from .input_listener import KeyboardListener


class DmicProcessManager:
    """Facade for controlling process manager components."""

    def __init__(self, client, uds_server, config_loader):
        self._client = client
        self.config_loader = config_loader
        self._app_handler = DmicApplicationHandler(self, config_loader)
        self._uds_server = uds_server
        self._timer = DmicTimer()
        self._sleep_manager = SleepManager(config_loader.global_config)
        self._key_listener = KeyboardListener(config_loader.global_config)

        self._interaction_feedback_active = False

        self._timer.alert_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.TIMEOUT, None))

        self._sleep_manager.notify_sleep_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.SLEEP, None))
        self._sleep_manager.woke_up_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.WAKE, None))

        # Reset timer when any button is pressed.
        self._key_listener.keyboard_triggered_event += lambda x: self._timer.reset()
        self._key_listener.keyboard_triggered_event += self._interaction_feedback_callback

        self._key_listener.menu_button_triggered_event += self._menu_button_callback
        self._key_listener.start()

    def send_to_ui(self, msg: str):
        self._uds_server.send(msg)

    def queue_state_task(self, task: DmicTask):
        self._client.queue_state_task(task)

    def queue_crash_notification(self, app_id):
        app_crashed_notification_task = DmicTask(DmicTaskType.APP_CRASHED, app_id)
        self.queue_state_task(app_crashed_notification_task)

    def start_app(self, app_id):
        self._app_handler.start_app(app_id)

    def verify_running(self, app_id):
        return self._app_handler.verify_running(app_id)

    def focus_app(self, app_id):
        self._app_handler.focus_app_sync(app_id)

    def verify_focus(self, app_id):
        return self._app_handler.verify_focus(app_id)

    def close_app(self, app_id):
        self._app_handler.close_app(app_id)

    def verify_closed(self, app_id):
        return self._app_handler.verify_closed(app_id)

    def _menu_button_callback(self, data):
        # Game id gets injected with the active apps name by the state machine.
        self.queue_state_task(DmicTask(DmicTaskType.CLOSE_APP, None))

    def _interaction_feedback_callback(self, data):
        if self._interaction_feedback_active:
            self.queue_state_task(DmicTask(DmicTaskType.INTERACTION, data))

    def set_interaction_feedback(self, is_on):
        self._interaction_feedback_active = is_on

    def set_timer(self, seconds):
        self._timer.set_timer(seconds)

    def stop_timer(self):
        self._timer.stop()

    def enter_sleep(self):
        self._sleep_manager.sleep_now()
