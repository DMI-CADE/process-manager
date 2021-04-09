from .statemachine import DmicTask


class DmicProcessManager:
    """Facade for controlling process manager components."""

    def __init__(self, client, uds_server, timer):
        self._client = client
        self._window_handler = None
        self._uds_server = uds_server
        self._timer = timer

    def send_to_ui(self, msg: str):
        self._uds_server.send(msg)

    def queue_state_task(self, task: DmicTask):
        self._client.queue_state_task(task)

    def start_app(self, app_id):
        pass

    def focus_app(self, app_id):
        pass

    def close_app(self, app_id):
        pass

    def set_timer(self, time):
        pass

    def get_elapsed_time(self):
        pass

    def stop_timer(self):
        pass
