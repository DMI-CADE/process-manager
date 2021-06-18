import logging
import threading

from .helper import DmicEvent


class DmicTimer:
    """Timer class for handling timeouts."""

    def __init__(self):
        self.timer_thread = threading.Timer(0, None)
        self.alert_event = DmicEvent()
        self._current_timer_length = 0

    def set_timer(self, seconds: int, log=True):
        """Starts the timer with given seconds."""

        self.stop(log)
        if log:
            logging.debug(f'[TIMER] Set timer to ({seconds})s.')

        self._current_timer_length = seconds

        self.timer_thread = threading.Timer(seconds, self._timer_callback)
        self.timer_thread.name = 'dmic_timer_thread'
        self.timer_thread.start()

    def _timer_callback(self):
        """Callback function for when the timer runs out.

        Triggers alert event.
        """

        logging.info(f'[TIMER] Timer ran out! ({self._current_timer_length})s')
        self.alert_event.update()

    def reset(self):
        """Resets the timer to previously set seconds."""

        # logging.debug('[TIMER] Reset timer...')
        self.set_timer(self._current_timer_length, False)

    def stop(self, log=True):
        """Stops the timer."""

        if log:
            logging.debug('[TIMER] Stop timer.')
        self.timer_thread.cancel()
