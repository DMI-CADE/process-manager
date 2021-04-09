from .statemachine import DmicTask


class DmicProcessManager:
    """Facade for controlling process manager components."""

    def __init__(self, client):
        self._client = client

    def queue_state_task(self, task: DmicTask):
        self._client.queue_state_task(task)
