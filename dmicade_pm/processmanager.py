from .tasks import DmicTask, DmicTaskType
from .application_handler import DmicApplicationHandler
from .timer import DmicTimer, SleepManager
from .input_listener import KeyboardListener
from .sound_manager import VolumeController
from .button_controller import DmicButtonController
from .serial_connection import DmicSerialConnector


class DmicProcessManager:
    """Facade for controlling process manager components."""

    def __init__(self, client, uds_server, config_loader):
        self._client = client
        self.config_loader = config_loader
        self._app_handler = DmicApplicationHandler(self, config_loader)
        self._uds_server = uds_server
        self._timeout_timer = DmicTimer()
        self._dyn_volume_timer = DmicTimer()
        self._sleep_manager = SleepManager(config_loader.global_config)
        self._key_listener = KeyboardListener(config_loader.global_config)
        self._volume_controller = VolumeController()
        self._serial_connector = DmicSerialConnector(port=config_loader.global_config['serial_port'])
        self._button_controller = DmicButtonController(config_loader.global_config, self._serial_connector)

        self._interaction_feedback_active = False

        self._timeout_timer.alert_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.TIMEOUT, None))
        self._dyn_volume_timer.alert_event += self._lower_volume # Violates state model.

        self._sleep_manager.notify_sleep_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.SLEEP, None))
        self._sleep_manager.woke_up_event += lambda x: self.queue_state_task(DmicTask(DmicTaskType.WAKE, None))

        # Reset timer when any button is pressed.
        self._key_listener.keyboard_triggered_event += lambda x: self._timeout_timer.reset()
        self._key_listener.keyboard_triggered_event += self._adjust_volume_on_interaction # Violates state model.
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

    def set_interaction_feedback(self, is_on: bool):
        self._interaction_feedback_active = is_on

    def set_timer(self, seconds: int):
        self._timeout_timer.set_timer(seconds)

    def stop_timer(self):
        self._timeout_timer.stop()

    def enter_sleep(self):
        self._sleep_manager.sleep_now()

    def is_sleep_time(self):
        return self._sleep_manager.is_sleep_time()

    def fade_volume(self, goal_perc, fade_duration):
        self._volume_controller.fade_volume(goal_perc, fade_duration)

    def set_volume(self, perc):
        self._volume_controller.set_volume(perc)

    def set_volume_timer(self, seconds):
        self._dyn_volume_timer.set_timer(seconds)

    def set_button_colors(self, color_data):
        self._button_controller.change_colors(color_data)

    def queue_clear_button_colors(self):
        self._button_controller.queue_clear()

    def queue_menu_button_led_state(self, is_on:bool):
        self._button_controller.queue_menu_button_state(is_on)

    # Following functions violate the state model... But it had to be done...

    def _adjust_volume_on_interaction(self, data):

        # Add up fade duration to start counter when high volume reched.
        if self.is_sleep_time():
            self._dyn_volume_timer.set_timer(
                int(self.config_loader.global_config['volume_up_fade_duration']) +
                int(self.config_loader.global_config['volume_time_until_lowering_in_sleephours']),
                False)
        else:
            self._dyn_volume_timer.set_timer(
                int(self.config_loader.global_config['volume_up_fade_duration']) +
                int(self.config_loader.global_config['volume_time_until_lowering']),
                False)

        self.fade_volume(
            int(self.config_loader.global_config['volume_perc_high']),
            int(self.config_loader.global_config['volume_up_fade_duration']))

    def _lower_volume(self, data):
        if self.is_sleep_time():
            self.fade_volume(
                int(self.config_loader.global_config['volume_perc_low']),
                int(self.config_loader.global_config['volume_down_fade_duration_in_sleephours']))
        else:
            self.fade_volume(
                int(self.config_loader.global_config['volume_perc_low']),
                int(self.config_loader.global_config['volume_down_fade_duration']))
