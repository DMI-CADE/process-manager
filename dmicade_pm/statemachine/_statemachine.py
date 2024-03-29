import logging
import time

from ._states import DmicStatePool
from ..tasks import DmicTask, DmicTaskType
from ..temperature_logging import DmicTemperatureLogging

class DmicStateMachine:
    """Statemachine of the processmanager.

    Has an active state to handle tasks and a task queue. The event
    loop handles task execution generally by delegating it to the
    active state.
    """

    TASK_CHECK_DELAY = 0.05

    def __init__(self, global_conf=None):
        self._state_pool = DmicStatePool()
        self._current_state = self._state_pool.get_object('start')
        self._task_queue = []
        self._is_running = False
        self._active_app = None

        self._gconf = global_conf # TEMPLOGGING
        self.temp_logging = DmicTemperatureLogging(self._gconf) # TEMPLOGGING

    def run_event_loop_sync(self):
        """Runs synchronous state machine loop.

        Waits for tasks to be queued, manages queued tasks and hands
        them to the current state to handle.
        """

        self._is_running = True

        self._current_state.enter()

        while self._is_running:
            if len(self._task_queue) > 0:
                logging.debug(f"""[STATEM] Task is queued:\n |- self._current_state={type(self._current_state).__name__}\n |- Tasks: {[n.type for n in self._task_queue]}""")
                task_is_ready = self._ready_task_buffer()

                if task_is_ready:
                    self._execute_next_task()
                    logging.debug('[STATEM] Task Done!\n')

            else:
                time.sleep(self.TASK_CHECK_DELAY)

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

        if logging.root.level <= logging.INFO:
            print()
        logging.info(f'[STATEM] Execute Task: {current_task.type.name}, {current_task.data}')

        if current_task.type is DmicTaskType.WAKE: # TEMPLOGGING
            self.temp_logging = DmicTemperatureLogging(self._gconf) # TEMPLOGGING

        if current_task.type is DmicTaskType.SET_ACTIVE_APP:
            self._active_app = current_task.data
        elif current_task.type is DmicTaskType.CHANGE_STATE:
            self._change_state(current_task.data)
        else:
            # Inject active apps name into task data while 'InGame'.
            if self._current_state == self._state_pool.get_object('ingame') and not current_task.data:
                current_task.data = self._active_app

            self._current_state.handle(current_task)

        self._task_queue.remove(current_task)
        logging.debug(f'[STATEM] Removed task, new queue: {[n.type for n in self._task_queue]}')

    def _change_state(self, state_name: str):
        """Handles steps to change to the next state."""

        # Only change state if state is different.
        if self._current_state == self._state_pool.get_object(state_name):
            return

        logging.debug('[STATEM] Exit state...')
        self._current_state.exit()

        logging.info(f'[STATEM] Change state to {state_name}.')
        logging.getLogger('temp_logger').info(f'Change state to {state_name}.') # TEMPLOGGING
        if state_name == 'sleep': # TEMPLOGGING
            self.temp_logging.stop() # TEMPLOGGING
            self.temp_logging = None  # TEMPLOGGING
        self._current_state = self._state_pool.get_object(state_name)
        logging.debug(f'[STATEM] Enter state: {self._current_state}')
        self._current_state.enter()

    def _ready_task_buffer(self):
        return len(self._task_queue) > 0
