import logging

from ._states import DmicStatePool
from ..tasks import DmicTask, DmicTaskType


class DmicStateMachine:
    """Statemachine of the processmanager.

    Has an active state to handle tasks and a task queue. The event
    loop handles task execution generally by delegating it to the
    active state.
    """

    def __init__(self, command_pool):
        self._state_pool = DmicStatePool(command_pool)
        self._current_state = self._state_pool.get_object('start')
        self._task_queue = []
        self._is_running = False

    def run_event_loop_sync(self):
        """Runs synchronous state machine loop.

        Waits for tasks to be queued, manages queued tasks and hands
        them to the current state to handle.
        """

        self._is_running = True

        self._current_state.enter()

        while self._is_running:
            if len(self._task_queue) > 0:
                logging.debug(f"""[STATEM] Task is queued:\n |- {self._current_state=}\n |- Tasks: {[n.type for n in self._task_queue]}""")
                task_is_ready = self._ready_task_buffer()

                if task_is_ready:
                    logging.debug('[STATEM] Execute Task...')
                    self._execute_next_task()
                    logging.debug('[STATEM] Task Done!')

    def stop_event_loop(self):
        """Stops event loop.

        Tells the event loop to exit after executing current task.
        """

        logging.info('[STATEM] Stop event loop...')
        self._is_running = False

    def queue_task_for_state(self, task: DmicTask):
        """Queues a task to be handled by the current state.

        Args:
          task: dict
            The task to queue.
        """

        logging.debug(f'[STATEM] Queue: {task.type}, {task.data=}')
        self._task_queue.append(task)
        logging.debug(f'[STATEM] {[n.type for n in self._task_queue]}')

    def _execute_next_task(self):
        """Handles execution of the next queued task."""

        current_task = self._task_queue[0]
        logging.info(f'[STATEM] Execute Task: {current_task.type.name}, {current_task.data}')

        if current_task.type is DmicTaskType.CHANGE_STATE:
            self._change_state(current_task.data)

        else:
            self._current_state.handle(current_task)

        self._task_queue.remove(current_task)
        logging.debug(f'[STATEM] Removed task, new queue: {[n.type for n in self._task_queue]}')

    def _change_state(self, state_name: str):
        """Handles steps to change to the next state."""

        logging.debug('[STATEM] Exit state...')
        self._current_state.exit()

        logging.info(f'[STATEM] Change state to {state_name}.')
        self._current_state = self._state_pool.get_object(state_name)
        logging.debug(f'[STATEM] Enter state: {self._current_state}')
        self._current_state.enter()

    def _ready_task_buffer(self):
        return len(self._task_queue) > 0
