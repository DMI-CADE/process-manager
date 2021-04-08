from ._states import DmicStatePool
from ._tasks import DmicTaskType


class DmicStateMachine:
    """Statemachine of the processmanager.

    Methods
    -------
    run_event_loop_sync()
        Runs synchronous state machine loop.
    stop_event_loop()
        Stops event loop.
    queue_task_for_state(task: dict)
        Queues a task to be handled by the current state.
    """

    def __init__(self, command_pool):
        self._state_pool = DmicStatePool(command_pool)
        self._current_state = self._state_pool.get_object('start')
        self._task_queue = []
        self._is_running = False

    def run_event_loop_sync(self):
        """Runs synchronous state machine loop.

        Waits for tasks to be queued, manages queued tasks and hands
        them to the current state to handle."""

        self._is_running = True

        while self._is_running:
            if len(self._task_queue) > 0:
                task_is_ready = self._ready_task_buffer()

                if task_is_ready:
                    self._execute_next_task()

    def stop_event_loop(self):
        """Stops event loop.

        Tells the event loop to exit after executing current task."""

        self._is_running = False

    def queue_task_for_state(self, task: dict):
        """Queues a task to be handled by the current state.

        Parameters
        ----------
        task : dict
            The task to queue.
        """

        self._task_queue.append(task)

    def _execute_next_task(self):
        current_task = self._task_queue[0]

        if current_task['type'] is DmicTaskType.CHANGE_STATE:
            self._change_state(current_task['data'])

        else:
            self._current_state.handle(current_task)

        self._task_queue.remove(current_task)

    def _change_state(self, state_name: str):
        self._current_state.exit()
        if not self._state_pool.object_exists(state_name):
            raise Exception('[DMIC STATE MACHINE] Unknown State')
        self._current_state = self._state_pool.get_object(state_name)
        self._current_state.enter()

    def _ready_task_buffer(self):
        return len(self._task_queue) > 0
